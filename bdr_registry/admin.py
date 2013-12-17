import logging
from cStringIO import StringIO
import csv
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
from django.http import HttpResponse
import requests
import models
from ldap_editor import create_ldap_editor
import audit

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



class ReadOnlyAdmin(admin.ModelAdmin):


    def get_actions(self, request):

        actions = super(ReadOnlyAdmin, self).get_actions(request)
        if self._user_is_readonly(request):
            actions = []
        return actions

    def change_view(self, request, object_id, extra_context=None):

        if self._user_is_readonly(request):
            self.readonly_fields = self.user_readonly
            self.inlines = self.user_readonly_inlines

            extra_context = extra_context or {}

        else:
            self.readonly_fields = []
            self.inlines = []

        return super(ReadOnlyAdmin, self).change_view(
            request, object_id, extra_context=extra_context)

    def _user_is_readonly(self, request):
        groups = [ x.name for x in request.user.groups.all() ]

        return "readonly" in groups


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
    mail_from = settings.BDR_EMAIL_FROM
    for organisation in organisations:
        for person in organisation.people.all():
            if organisation.obligation.code == 'ods':
                subject = u"Reporting data on ODS covering 2012"
                html = render_to_string('email_organisation_ods.html', {
                    'person': person,
                    'organisation': organisation,
                })
                mail_bcc = settings.BDR_ORGEMAIL_ODS_BCC

            elif organisation.obligation.code == 'fgas':
                subject = u"Reporting data on F-Gases covering 2012"
                html = render_to_string('email_organisation_fgas.html', {
                    'person': person,
                    'organisation': organisation,
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
        form = {
            'country_code': org.country.code,
            'obligation_folder_name': org.obligation.reportek_slug,
            'account_uid': org.account.uid,
            'organisation_name': org.name,
        }
        audit.log("Creatig zope folder for uid=%s", org.account.uid)
        resp = requests.post(url, data=form, auth=settings.BDR_API_AUTH)
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


class PersonInline(admin.StackedInline):

    model = models.Person
    extra = 0


class PersonReadOnlyInline(PersonInline):

    readonly_fields = ['title', 'family_name', 'first_name', 'email',
                       'email2', 'phone', 'phone2', 'phone3', 'fax', 'organisation']


class OrganisationAdmin(ReadOnlyAdmin):

    user_readonly = ['EORI_LABEL', 'name', 'date_registered', 'active',
                     'addr_street', 'addr_place1', 'addr_postalcode',
                     'addr_place2', 'eori', 'vat_number', 'country',
                     'obligation', 'account', 'comments']
    user_readonly_inlines = [PersonReadOnlyInline]

    list_filter = ['obligation', 'country']
    list_display = ['__unicode__', 'obligation', 'account', 'country',
                    'addr_postalcode', 'vat_number', 'eori']
    search_fields = ['name', 'account__uid', 'addr_postalcode',
                     'vat_number', 'eori']
    actions = [create_accounts, reset_password, send_password_email,
               create_reporting_folder]

    inlines = [PersonInline]

    def get_urls(self):
        my_urls = patterns('',
            (r'^(?P<pk>\d+)/name_history/$',
                self.admin_site.admin_view(self.name_history)),
            (r'^export$', self.admin_site.admin_view(self.export)),
        )
        return my_urls + super(OrganisationAdmin, self).get_urls()

    def name_history(self, request, pk):
        org = get_object_or_404(models.Organisation, pk=pk)
        return TemplateResponse(request, 'organisation_name_history.html', {
            'organisation': org,
            'opts': org._meta,
        }, current_app=self.admin_site.name)

    def export(self, request):
        of = StringIO()
        out = csv.writer(of)
        out.writerow(['userid', 'name', 'date_registered', 'active',
                      'addr_street', 'addr_place1', 'addr_postalcode',
                      'addr_place2', 'country', 'vat_number', 'obligation'])
        for org in models.Organisation.objects.all():
            account = org.account
            out.writerow([v.encode('utf-8') for v in [
                '' if account is None else account.uid,
                org.name,
                org.date_registered.strftime('%Y-%m-%d %H:%M:%S'),
                'on' if org.active else '',
                org.addr_street,
                org.addr_place1,
                org.addr_postalcode,
                org.addr_place2,
                org.country.name,
                org.vat_number or '',
                org.obligation.code if org.obligation else '',
            ]])
        return HttpResponse(of.getvalue(), content_type="text/plain")


class PersonAdmin(ReadOnlyAdmin):

    user_readonly = ['title', 'family_name', 'first_name',
                     'email', 'email2', 'phone', 'phone2', 'phone3',
                     'fax', 'organisation']

    user_readonly_inlines = []

    search_fields = ['first_name', 'family_name', 'email', 'phone', 'fax',
                     'organisation__name', 'organisation__account__uid']

    def get_urls(self):
        my_urls = patterns('',
            (r'^export$', self.admin_site.admin_view(self.export)),
        )
        return my_urls + super(PersonAdmin, self).get_urls()

    def export(self, request):
        of = StringIO()
        out = csv.writer(of)
        out.writerow(['userid', 'companyname', 'country',
                      'contactname', 'contactemail'])
        for person in models.Person.objects.all():
            org = person.organisation
            account = org.account
            if account is None:
                continue
            out.writerow([v.encode('utf-8') for v in [
                account.uid,
                org.name,
                org.country.name,
                u"{p.title} {p.first_name} {p.family_name}".format(p=person),
                person.email,
            ]])
        return HttpResponse(of.getvalue(), content_type="text/plain")


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
