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
        org = models.Organisation.objects.create(**org_data)

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

        p1 = models.Person.objects.create(organisation=org, **p1_data)
        if any(p2_data.values()):
            p2 = models.Person.objects.create(organisation=org, **p2_data)


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

        org = models.Organisation.objects.create(
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
