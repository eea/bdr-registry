from collections import defaultdict
from io import BytesIO
from post_office import mail
from post_office.connections import connections

import xlwt

from django.conf import settings

from bdr_registry.ldap_editor import create_ldap_editor
from bdr_registry.models import SiteConfiguration
from bdr_registry.views import valid_email


def sync_accounts_with_ldap(accounts, person=None):
    if hasattr(settings, "DISABLE_LDAP_CONNECTION"):
        return

    ldap_editor = create_ldap_editor()
    counters = defaultdict(int)
    for account in accounts:
        if person:
            company = account.persons.first()
        else:
            company = account.companies.first()
        if ldap_editor.create_account(
            account.uid, company.name, company.country.name, account.password
        ):
            counters["create"] += 1
        else:
            ldap_editor.reset_password(account.uid, account.password)
            counters["password"] += 1
    return dict(counters)


def send_password_email_to_people(
    company,
    url=None,
    person=None,
    company_account=None,
    use_reset_url=None,
    send_bcc=True,
    subject_extra="",
    set_owner=None,
    password_reset=None,
    personal_account=None,
):
    connections.close()
    config = SiteConfiguration.objects.get()
    template = company.obligation.email_template
    bcc = company.obligation.bcc.split(",")
    bcc = [s.strip() for s in bcc if valid_email(s.strip())]
    if company.obligation.code == "hdv":
        sender = settings.HDV_EMAIL_FROM
    elif company.obligation.code == "hdv_resim":
        sender = settings.HDV_RESIM_EMAIL_FROM
    else:
        sender = settings.BDR_EMAIL_FROM
    if not send_bcc:
        bcc = []
    if company_account:
        reporting_year = config.reporting_year
        mail.send(
            recipients=[person.email.strip()],
            bcc=bcc,
            sender=sender,
            template=template,
            context={
                "company": company,
                "person": person,
                "account": company.account,
                "url": url,
                "set_owner": set_owner,
                "password_reset": password_reset,
                "personal_account": personal_account,
                "subject_extra": subject_extra,
                "reporting_year": reporting_year,
                "use_reset_url": use_reset_url,
                "next_year": reporting_year + 1,
            },
            priority="now",
        )
        return 1
    if person:
        reporting_year = config.reporting_year
        mail.send(
            recipients=[person.email.strip()],
            bcc=bcc,
            sender=sender,
            template=template,
            context={
                "company": company,
                "person": person,
                "account": person.account,
                "url": url,
                "set_owner": set_owner,
                "password_reset": password_reset,
                "subject_extra": subject_extra,
                "reporting_year": reporting_year,
                "use_reset_url": use_reset_url,
                "personal_account": True,
                "next_year": reporting_year + 1,
            },
            priority="now",
        )
        return 1
    for person in company.people.all():
        reporting_year = config.reporting_year
        mail.send(
            recipients=[person.email.strip()],
            bcc=bcc,
            sender=sender,
            template=template,
            context={
                "company": company,
                "person": person,
                "account": company.account,
                "url": url,
                "set_owner": set_owner,
                "password_reset": password_reset,
                "personal_account": personal_account,
                "subject_extra": subject_extra,
                "use_reset_url": use_reset_url,
                "reporting_year": reporting_year,
                "next_year": reporting_year + 1,
            },
            priority="now",
        )
    connections.close()
    return company.people.count()


def generate_excel(header, rows):
    style = xlwt.XFStyle()
    normalfont = xlwt.Font()
    headerfont = xlwt.Font()
    headerfont.bold = True
    style.font = headerfont
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Sheet 1")
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
