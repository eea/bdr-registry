from collections import defaultdict

from django.conf import settings
from django.template.loader import render_to_string
from django.core import mail

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


def send_password_email_to_people(organisations):
    n = 0
    mail_from = settings.BDR_EMAIL_FROM
    reporting_year = settings.REPORTING_YEAR
    for organisation in organisations:
        for person in organisation.people.all():
            if organisation.obligation.code == 'ods':
                subject = u"Reporting data on ODS covering %s" % reporting_year
                html = render_to_string('email_organisation_ods.html', {
                    'person': person,
                    'organisation': organisation,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_ODS_BCC

            elif organisation.obligation.code == 'fgas':
                subject = u"Reporting data on F-Gases covering %s" % (
                    reporting_year)
                html = render_to_string('email_organisation_fgas.html', {
                    'person': person,
                    'organisation': organisation,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_FGAS_BCC

            else:
                raise RuntimeError("Unknown obligation %r" %
                                   organisation.obligation.code)

            mail_to = [person.email]
            message = mail.EmailMessage(subject, html,
                                        mail_from, mail_to, mail_bcc)
            message.content_subtype = 'html'
            message.send(fail_silently=False)
            n += len(mail_to)

    return n
