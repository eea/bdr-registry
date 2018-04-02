from collections import defaultdict

from io import BytesIO
import xlwt

from django.core.urlresolvers import reverse

from django.conf import settings
from post_office import mail

from bdr_registry.ldap_editor import create_ldap_editor
from bdr_registry.models import SiteConfiguration


def sync_accounts_with_ldap(accounts):
    if hasattr(settings, 'DISABLE_LDAP_CONNECTION'):
        return

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
    raise DeprecationWarning


def send_registration_email(person):
    config = SiteConfiguration.objects.get()
    company = person.company
    account = person.account
    template = config.register_new_account

    token_url = reverse(
        'person_register',
        kwargs=dict(
            pk=person.pk,
            token=account.get_registration_token()
        )
    )

    mail.send(
        recipients=[person.email.strip()],
        sender=settings.BDR_EMAIL_FROM,
        template=template,
        priority='now',
        context=dict(
            company=company,
            person=person,
            registration_url=token_url,
        )
    )


def generate_excel(header, rows):
    style = xlwt.XFStyle()
    normalfont = xlwt.Font()
    headerfont = xlwt.Font()
    headerfont.bold = True
    style.font = headerfont
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet 1')
    row = 0

    for col in range(0, len(header)):
        ws.row(row).set_cell_text(col, header[col], style)

    style.font = normalfont

    for item in rows:
        row += 1
        for col in range(0, len(item)):
            ws.row(row).set_cell_text(col, item[col], style)
    output = BytesIO()
    wb.save(output)

    return output.getvalue()
