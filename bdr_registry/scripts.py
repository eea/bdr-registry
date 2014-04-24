import logging
import csv
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from . import models


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


HOURS_2 = timedelta(hours=2)


@transaction.commit_on_success
def import_companies(csv_file):
    for byte_row in csv.DictReader(csv_file):
        row = {k: byte_row[k].decode('utf-8') for k in byte_row}

        country = models.Country.objects.get(name=row['Country'])
        obligation = models.Obligation.objects.get(code=row['Obligation'])
        raw_date = datetime.strptime(row['Registered'], '%Y-%m-%d %H:%M:%S')
        account = models.Account.objects.create(uid=row['UserID'])
        org_data = {
            'account': account,
            'date_registered': timezone.make_aware(raw_date - HOURS_2,
                                                   timezone.utc),
            'obligation': obligation,
            'name': row['Organisation'],
            'country': country,
            'addr_place2': row['Region'],
            'addr_place1': row['Municipality'],
            'addr_street': row['Street'],
            'addr_postalcode': row['PostalCode'],
        }
        org = models.Company.objects.create(**org_data)

        p1_data = {
            'title': row['p1-Title'],
            'family_name': row['p1-Surname'],
            'first_name': row['p1-Given'],
            'email': row['p1-Email'],
            'phone': row['p1-Phone'],
            'fax': row['p1-Fax'],
        }

        p2_data = {
            'title': row['p2-Title'],
            'family_name': row['p2-Surname'],
            'first_name': row['p2-Given'],
            'email': row['p2-Email'],
            'phone': row['p2-Phone'],
            'fax': row['p2-Fax'],
        }

        p1 = models.Person.objects.create(company=org, **p1_data)
        if any(p2_data.values()):
            p2 = models.Person.objects.create(company=org, **p2_data)


@transaction.commit_on_success
def update_companies_from_ldap():
    import ldap
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    res = conn.search_s("ou=Business Reporters,o=Eionet,l=Europe",
                        ldap.SCOPE_SUBTREE,
                        '(objectClass=organizationalRole)')
    for dn, attrs in res:
        [uid] = attrs['uid']
        [cn] = attrs['cn']
        org_name, country_name = [v.strip().decode('utf-8')
                                  for v in cn.rsplit('/', 1)]
        account, is_new = models.Account.objects.get_or_create(uid=uid)
        if not is_new:
            log.debug("Account uid=%r already in db, skipping.", uid)
            continue

        country = models.Country.objects.get(name=country_name.title())

        if uid.startswith('fgas'):
            obligation = models.Obligation.objects.get(code='fgas')
        elif uid.startswith('ods'):
            obligation = models.Obligation.objects.get(code='ods')
        else:
            log.warn("Can't determine obligation for uid=%r", uid)
            continue

        org = models.Company.objects.create(
            name=org_name,
            addr_street="",
            addr_place1="",
            addr_postalcode="",
            addr_place2="",
            country=country,
            obligation=obligation,
            account=account)

        log.info("Organisation: uid=%r pk=%r name=%r",
                 org.account.uid, org.pk, org.name)


@transaction.commit_on_success
def update_companies_from_csv(csv_file, commit=False):
    for byte_row in csv.DictReader(csv_file, dialect='excel-tab'):
        row_dict = {k: byte_row[k].decode('utf-8') for k in byte_row}
        def row(*keys):
            for k in keys:
                if k in row_dict:
                    return row_dict[k]
            else:
                raise RuntimeError('No key matches: %r', keys)
        uid = row('Userid', 'UserID')
        try:
            account = models.Account.objects.get(uid=uid)
        except models.Account.DoesNotExist:
            log.warn("uid=%s: not found", uid)
            continue
        org = models.Company.objects.get(account=account)

        old = [org.addr_street, org.addr_place1,
               org.addr_place2, org.addr_postalcode]
        new = [row('address', 'Address', 'Street'),
               row('Place', 'City', 'Municipality'),
               '',
               row('Postal code', 'PostalCode')]
        if old != new:
            org.addr_street = row('address', 'Address', 'Street')
            org.addr_place1 = row('Place', 'City', 'Municipality')
            org.addr_postalcode = row('Postal code', 'PostalCode')
            org.save()
            log.info("uid=%s: update address", account.uid)

        count = org.people.count()
        if count > 0:
            log.warn("uid=%s: removing %d existing people", account.uid, count)
            org.people.all().delete()

        for n in range(1, 3):
            person_data = {
                'first_name': row('CP%d - first name' % n,
                                  'first name C%d' % n,
                                  'Given_%d' % n),
                'family_name': row('CP%d - Last name' % n,
                                   'last name C%d' % n,
                                   'Surname_%d' % n),
                'email': row('CP%d - e-mail' % n,
                             'Email C%d' % n,
                             'Email_%d' % n),
                'phone': row('CP%d - Tel' % n,
                             'Tel C%d' % n if n > 1 else 'Org Tel C%d' % n,
                             'Phone_%d' % n),
                'fax': row('CP%d - Fax' % n,
                           'Fax C%d' % n if n > 1 else 'Org Fax C%d' % n,
                           'Fax_%d' % n),
            }
            if not any(person_data.values()):
                continue

            if not person_data['phone'] and row_dict.get('phone'):
                person_data['phone'] = row('phone')

            if not person_data['fax'] and row_dict.get('fax'):
                person_data['fax'] = row('fax')

            org.people.create(**person_data)
            log.info("uid=%s: new person email=%s",
                     account.uid, person_data['email'])

    if not commit:
        log.warn("Rolling back transaction")
        transaction.rollback()
