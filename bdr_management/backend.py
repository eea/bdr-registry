from collections import defaultdict

from django.conf import settings
from post_office import mail

from bdr_registry.ldap_editor import create_ldap_editor


def sync_accounts_with_ldap(accounts):
    ldap_editor = create_ldap_editor()
    counters = defaultdict(int)
    for account in accounts:
        if ldap_editor.create_account(account.uid,
                                      account.company.name,
                                      account.company.country.name,
                                      account.password):
            counters['create'] += 1
        else:
            ldap_editor.reset_password(account.uid, account.password)
            counters['password'] += 1
    return dict(counters)


def send_password_email_to_people(company):

    template = company.obligation.email_template
    for person in company.people.all():
        mail.send([person.email],
                  settings.BDR_EMAIL_FROM,
                  template=template,
                  context={'company': company, 'person': person},
                  priority='now')

    return company.people.count()
