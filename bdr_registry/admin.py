import logging
from collections import defaultdict
from django.contrib import admin
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.admin import helpers
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.conf.urls import patterns
from django.shortcuts import get_object_or_404
import requests
import models
from ldap_editor import create_ldap_editor
import audit

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def sync_accounts_with_ldap(accounts):
    ldap_editor = create_ldap_editor()
    counters = defaultdict(int)
    for account in accounts:
        if ldap_editor.create_account(account.uid,
                                      account.organisation.name,
                                      account.organisation.country.name,
                                      account.password):
            counters['create'] += 1
        else:
            ldap_editor.reset_password(account.uid, account.password)
            counters['password'] += 1
    return dict(counters)


def sync_with_ldap(modeladmin, request, queryset):
    counters = sync_accounts_with_ldap(queryset)
    msg = "LDAP: %r." % (counters,)
    messages.add_message(request, messages.INFO, msg)


def create_accounts(modeladmin, request, queryset):
    organisations_without_account = [o for o in queryset if o.account is None]

    if request.POST.get('perform_create'):
        n = 0
        new_accounts = []
        for organisation in organisations_without_account:
            obligation = organisation.obligation
            account = models.Account.objects.create_for_obligation(obligation)
            account.set_random_password()
            organisation.account = account
            new_accounts.append(account)
            organisation.save()
            n += 1
        counters = sync_accounts_with_ldap(new_accounts)
        msg = "Created %d accounts. LDAP: %r." % (n, counters)
        messages.add_message(request, messages.INFO, msg)

        if request.POST.get('email'):
            return send_password_email(modeladmin, request,
                                       organisations_without_account)

        return

    return TemplateResponse(request, 'organisation_create_accounts.html', {
        'organisations_without_account': organisations_without_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


def reset_password(modeladmin, request, queryset):
    organisations_with_account = [o for o in queryset if o.account is not None]

    if request.POST.get('perform_reset'):
        n = 0
        reset_accounts = []
        for organisation in organisations_with_account:
            organisation.account.set_random_password()
            reset_accounts.append(organisation.account)
            n += 1
        counters = sync_accounts_with_ldap(reset_accounts)
        msg = "%d passwords have been reset. LDAP: %r." % (n, counters)
        messages.add_message(request, messages.INFO, msg)

        if request.POST.get('email'):
            return send_password_email(modeladmin, request, queryset)

        return

    return TemplateResponse(request, 'organisation_reset_password.html', {
        'organisations_with_account': organisations_with_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


def send_password_email_to_people(organisations):
    n = 0
    for organisation in organisations:
        mail_from = settings.BDR_EMAIL_FROM
        mail_to = [person.email for person in organisation.people.all()]
        html = render_to_string('organisation_password_mail.html', {
            'organisation': organisation,
        })
        message = mail.EmailMessage("BDR password reminder",
                                    html, mail_from, mail_to)
        message.content_subtype = 'html'
        message.send(fail_silently=False)
        n += len(mail_to)

    return n


def send_password_email(modeladmin, request, queryset):
    organisations_with_account = [o for o in queryset if o.account is not None]

    if request.POST.get('perform_send'):
        n = send_password_email_to_people(organisations_with_account)
        messages.add_message(request, messages.INFO,
                             "Emails have been sent to %d people." % n)
        return

    return TemplateResponse(request, 'organisation_email_password.html', {
        'organisations_with_account': organisations_with_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


def create_reporting_folder(modeladmin, request, queryset):
    if not (settings.BDR_API_URL and settings.BDR_API_AUTH):
        messages.add_message(request, messages.ERROR,
                             "BDR_API_URL and BDR_API_AUTH not configured")
        return

    created = []
    existing = []
    errors = []

    for org in queryset:
        url = settings.BDR_API_URL + '/create_organisation_folder'
        auth = tuple(settings.BDR_API_AUTH.split(':', 1))
        form = {
            'country_code': org.country.code,
            'obligation_code': org.obligation.code,
            'account_uid': org.account.uid,
            'organisation_name': org.name,
        }
        audit.log("Creatig zope folder for uid=%s", org.account.uid)
        resp = requests.post(url, data=form, auth=auth)
        if resp.status_code != 200:
            logging.error("BDR API request failed: %r", resp)
            errors.append(org.account.uid)
            continue

        rv = resp.json()
        success = rv['success']
        if success:
            if rv['created']:
                created.append(rv['path'])
            else:
                existing.append(rv['path'])
        else:
            msg = "%s: %s" % (org.account.uid, rv['error'])
            messages.add_message(request, messages.ERROR, msg)

    if created:
        msg = "%d folders created: %s" % (len(created), ', '.join(created))
        messages.add_message(request, messages.INFO, msg)

    if existing:
        msg = "%d already existing: %s" % (len(existing), ', '.join(existing))
        messages.add_message(request, messages.INFO, msg)

    if errors:
        msg = "%d errors: %s" % (len(errors), ', '.join(errors))
        messages.add_message(request, messages.ERROR, msg)


class OrganisationAdmin(admin.ModelAdmin):

    list_filter = ['obligation', 'country']
    list_display = ['__unicode__', 'obligation', 'account', 'country']
    search_fields = ['name', 'account__uid']
    actions = [create_accounts, reset_password, send_password_email,
               create_reporting_folder]

    def get_urls(self):
        my_urls = patterns('',
            (r'^(?P<pk>\d+)/name_history/$',
                self.admin_site.admin_view(self.name_history)),
        )
        return my_urls + super(OrganisationAdmin, self).get_urls()

    def name_history(self, request, pk):
        org = get_object_or_404(models.Organisation, pk=pk)
        return TemplateResponse(request, 'organisation_name_history.html', {
            'organisation': org,
            'opts': org._meta,
        }, current_app=self.admin_site.name)


class PersonAdmin(admin.ModelAdmin):

    search_fields = ['first_name', 'family_name', 'email', 'phone', 'fax',
                     'organisation__name', 'organisation__account__uid']


class AccountAdmin(admin.ModelAdmin):

    actions = [sync_with_ldap]


admin.site.register(models.Country)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Obligation)
admin.site.register(models.ApiKey)
if settings.ADMIN_ALL_BDR_TABLES:
    admin.site.register(models.Account, AccountAdmin)
    admin.site.register(models.NextAccountId)
