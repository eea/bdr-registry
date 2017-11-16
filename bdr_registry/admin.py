import csv
import logging
import post_office
import requests
from io import StringIO
from collections import defaultdict

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.contrib.admin import helpers
from django.core import mail
from django.conf import settings
from django.conf.urls import url
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from bdr_registry import models
from .audit import log
from .ldap_editor import create_ldap_editor

from solo.admin import SingletonModelAdmin


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
            self.inlines = self._user_readonly_inlines
            extra_context = extra_context or {}

        else:
            self.inlines = self._inlines
            self.readonly_fields = []

        return super(ReadOnlyAdmin, self).change_view(
            request, object_id, extra_context=extra_context)

    def add_view(self, request, **kwargs):
        self.readonly_fields = []
        return super(ReadOnlyAdmin, self).add_view(request, **kwargs)

    def _user_is_readonly(self, request):
        groups = [ x.name for x in request.user.groups.all() ]

        return "readonly" in groups


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


def sync_with_ldap(modeladmin, request, queryset):
    counters = sync_accounts_with_ldap(queryset)
    msg = "LDAP: %r." % (counters,)
    messages.add_message(request, messages.INFO, msg)


def create_accounts(modeladmin, request, queryset):
    organisations_without_account = [o for o in queryset if o.account is None]

    if request.POST.get('perform_create'):
        n = 0
        new_accounts = []
        for company in organisations_without_account:
            obligation = company.obligation
            account = models.Account.objects.create_for_obligation(obligation)
            account.set_random_password()
            company.account = account
            new_accounts.append(account)
            company.save()
            n += 1
        # counters = sync_accounts_with_ldap(new_accounts)
        counters = 0
        msg = "Created %d accounts. LDAP: %r." % (n, counters)
        messages.add_message(request, messages.INFO, msg)

        if request.POST.get('email'):
            return send_password_email(modeladmin, request,
                                       organisations_without_account)

        return

    return TemplateResponse(request, 'company_create_accounts.html', {
        'organisations_without_account': organisations_without_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


def reset_password(modeladmin, request, queryset):
    organisations_with_account = [o for o in queryset if o.account is not None]

    if request.POST.get('perform_send'):
        return send_password_email(modeladmin, request, queryset)

    if request.POST.get('perform_reset'):
        n = 0
        reset_accounts = []
        for company in organisations_with_account:
            company.account.set_random_password()
            reset_accounts.append(company.account)
            n += 1
        counters = sync_accounts_with_ldap(reset_accounts)
        msg = "%d passwords have been reset. LDAP: %r." % (n, counters)
        messages.add_message(request, messages.INFO, msg)

        if request.POST.get('email'):
            return send_password_email(modeladmin, request, queryset)

        return

    return TemplateResponse(request, 'company_reset_password.html', {
        'organisations_with_account': organisations_with_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


def send_password_email_to_people(organisations):
    n = 0
    mail_from = settings.BDR_EMAIL_FROM
    reporting_year = settings.REPORTING_YEAR
    for company in organisations:
        for person in company.people.all():
            if company.obligation.code == 'ods':
                subject = u"Reporting data on ODS covering %s" % reporting_year
                html = render_to_string('email_company_ods.html', {
                    'person': person,
                    'company': company,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_ODS_BCC

            elif company.obligation.code == 'fgas':
                subject = u"Reporting data on F-Gases covering %s" % reporting_year
                html = render_to_string('email_company_fgas.html', {
                    'person': person,
                    'company': company,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_FGAS_BCC

            elif company.obligation.code == 'vans':
                subject = u"Reporting data on Average CO2 emissions (light commercial vehicles) %s" % reporting_year
                html = render_to_string('email_organisation_vans.html', {
                    'person': person,
                    'organisation': company,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_VANS_BCC

            elif company.obligation.code == 'cars':
                subject = u"Reporting data on Average CO2 emissions (passenger cars) covering %s" % reporting_year
                html = render_to_string('email_organisation_cars.html', {
                    'person': person,
                    'organisation': company,
                    'reporting_year': reporting_year,
                    'next_year': reporting_year + 1
                })
                mail_bcc = settings.BDR_ORGEMAIL_CARS_BCC

            else:
                raise RuntimeError("Unknown obligation %r" %
                                   company.obligation.code)

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

    return TemplateResponse(request, 'company_email_password.html', {
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
        log("Creating zope folder for uid=%s", org.account.uid)
        resp = requests.post(url, data=form, auth=settings.BDR_API_AUTH, verify=False)
        if resp.status_code != 200 or 'unauthorized' in resp.content.lower():
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
                       'phone', 'phone2', 'phone3', 'fax', 'company']


class CommentInline(admin.StackedInline):

    model = models.Comment
    extra = 0


class CommentReadOnlyInline(CommentInline):

    readonly_fields = ['text']


class CustomBooleanFieldListFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        super(CustomBooleanFieldListFilter, self).__init__(field,
            request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        for lookup, title in (
                (None, 'All'),
                ('1', 'without account'),
                ('0', 'with account')):
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: lookup,
                }),
                'display': title,
            }

admin.FieldListFilter.register(lambda f: isinstance(f,
    (models.OneToOneField)), CustomBooleanFieldListFilter)


class OrganisationAdmin(ReadOnlyAdmin):

    user_readonly = ['EORI_LABEL', 'name', 'date_registered', 'active',
                     'addr_street', 'addr_place1', 'addr_postalcode',
                     'addr_place2', 'website', 'eori', 'vat_number', 'country',
                     'obligation', 'comments']

    _user_readonly_inlines = [CommentReadOnlyInline, PersonReadOnlyInline]
    _inlines = [CommentInline, PersonInline]
    exclude = ('account',)

    list_filter = [
        ('date_registered', admin.DateFieldListFilter),
        ('account', CustomBooleanFieldListFilter),
        'obligation',
        'country'
    ]

    list_display = ['id', 'name', 'obligation', 'account', 'country',
                    'addr_postalcode', 'vat_number', 'eori']
    list_display_links = ('name',)

    search_fields = ['name', 'account__uid', 'addr_postalcode',
                     'vat_number', 'eori']
    actions = [create_accounts, reset_password, create_reporting_folder]

    def get_urls(self):
        my_urls = [
            url(r'^(?P<pk>\d+)/name_history/$',
                self.admin_site.admin_view(self.name_history)),
            url(r'^export$', self.admin_site.admin_view(self.export)),
        ]
        return my_urls + super(OrganisationAdmin, self).get_urls()

    def name_history(self, request, pk):
        org = get_object_or_404(models.Company, pk=pk)
        return TemplateResponse(request, 'company_name_history.html', {
            'company': org,
            'opts': org._meta,
        }, current_app=self.admin_site.name)

    def export(self, request):
        of = StringIO()
        out = csv.writer(of)
        out.writerow(['userid', 'name', 'date_registered', 'active',
                      'addr_street', 'addr_place1', 'addr_postalcode',
                      'addr_place2', 'country', 'vat_number', 'obligation'])
        for org in models.Company.objects.all():
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
                     'email', 'phone', 'phone2', 'phone3',
                     'fax', 'company']

    _user_readonly_inlines = []
    _inlines = []

    search_fields = ['first_name', 'family_name', 'email', 'phone', 'fax',
                     'organisation__name', 'organisation__account__uid']

    def get_urls(self):
        my_urls = [
            url(r'^export$', self.admin_site.admin_view(self.export)),
        ]
        return my_urls + super(PersonAdmin, self).get_urls()

    def export(self, request):
        of = StringIO()
        out = csv.writer(of)
        out.writerow(['userid', 'companyname', 'country',
                      'contactname', 'contactemail'])
        for person in models.Person.objects.all():
            org = person.company
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
admin.site.register(models.ApiKey)

admin.site.unregister(User)


class UserAdminForm(UserChangeForm):
    obligations = forms.ModelMultipleChoiceField(
        queryset=models.Obligation.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Obligations',
            is_stacked=False
        )
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['obligations'].initial = self.instance.obligations.all()

    def save(self, commit=True):
        user = super(UserAdminForm, self).save(commit=False)

        user.obligations = self.cleaned_data['obligations']

        if commit:
            user.save()
            user.save_m2m()

        return user


class CustomUserAdmin(UserAdmin):
    form = UserAdminForm
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'get_obligations',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Obligations'), {'fields': ('obligations',)}),
    )


User.get_obligations = (
    lambda self: '\n'.join(o.name for o in self.obligations.all())
)
admin.site.register(User, CustomUserAdmin)

if not settings.ADMIN_ALL_BDR_TABLES:
    admin.site.unregister(post_office.models.EmailTemplate)

if settings.ADMIN_ALL_BDR_TABLES:
    admin.site.register(models.Account, AccountAdmin)
    admin.site.register(models.NextAccountId)
    admin.site.register(models.Company, OrganisationAdmin)
    admin.site.register(models.Person, PersonAdmin)
    admin.site.register(models.Obligation)
    admin.site.register(models.SiteConfiguration, SingletonModelAdmin)
