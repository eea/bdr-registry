import django_settings
import requests
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views import generic
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect

from braces import views

from bdr_management.forms import PersonFormWithoutCompany
from bdr_management import base, forms, backend
from bdr_management.base import Breadcrumb
from bdr_management.forms.companies import CompanyForm, CompanyDeleteForm
from bdr_registry.models import Company, Account, ReportingYear, ReportingStatus


class Companies(views.StaffuserRequiredMixin,
                generic.TemplateView):

    template_name = 'bdr_management/companies.html'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Companies'))
        ]
        context = super(Companies, self).get_context_data(**kwargs)
        context['breadcrumbs'] = breadcrumbs
        context['form'] = forms.CompanyFilters()
        return context


class CompaniesFilter(views.StaffuserRequiredMixin,
                      base.FilterView):

    def process_name(self, object, val):
        url = reverse('management:companies_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def process_date_registered(self, object, val):
        return val.strftime(settings.DATE_FORMAT)

    def get_queryset(self, opt):
        queryset = Company.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(name__icontains=opt['search']) |
                Q(account__uid__icontains=opt['search']) |
                Q(addr_postalcode__icontains=opt['search']) |
                Q(vat_number__icontains=opt['search']) |
                Q(eori__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        filters = opt.get('filters', {})
        if 'country' in filters:
            queryset = queryset.filter(
                country__name=filters['country'])
        if 'obligation' in filters:
            queryset = queryset.filter(
                obligation__name=filters['obligation'])
        if 'account' in filters:
            if filters['account'] == forms.CompanyFilters.WITHOUT_ACCOUNT:
                queryset = queryset.exclude(account__isnull=False)
            else:
                queryset = queryset.exclude(account__isnull=True)
        if 'date_registered' in filters:
            start_date = self._get_startdate(filters['date_registered'])
            queryset = queryset.exclude(date_registered__lt=start_date)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]

    def _get_startdate(self, selected_option):
        today = date.today()
        if selected_option == forms.CompanyFilters.TODAY:
            start_date = today
        elif selected_option == forms.CompanyFilters.LAST_7_DAYS:
            start_date = today - timedelta(days=7)
        elif selected_option == forms.CompanyFilters.THIS_MONTH:
            start_date = date(today.year, today.month, 1)
        else:
            start_date = date(today.year, 1, 1)
        return start_date


class CompaniesBaseView(base.ModelTableViewMixin,
                        generic.DetailView):

    template_name = 'bdr_management/company_view.html'
    model = Company
    exclude = ('id', )

    def get_context_data(self, **kwargs):
        data = super(CompaniesBaseView, self).get_context_data()
        company = self.object
        statuses = company.reporting_statuses.filter(
            reporting_year__year__gte=settings.FIRST_REPORTING_YEAR).filter(
            reporting_year__year__lte=django_settings.get('Reporting year')
        )
        years = [unicode(stat.reporting_year) for stat in statuses
                 if stat.reported]
        data['reporting_years'] = years
        return data


class CompaniesManagementView(views.StaffuserRequiredMixin,
                              CompaniesBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:companies'),
                       _('Companies')),
            Breadcrumb('', self.object)
        ]
        data = super(CompaniesManagementView,
                     self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs

        data['person_add_url'] = reverse('management:persons_add',
                                         kwargs=self.kwargs)
        data['comment_add_url'] = reverse('management:comment_add',
                                          kwargs=self.kwargs)
        data['comment_delete_route'] = 'management:comment_delete'
        data['person_route'] = 'management:persons_view'
        data['management'] = True

        return data

    def get_edit_url(self):
        return reverse('management:companies_edit', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('management:companies_delete', kwargs=self.kwargs)

    def get_back_url(self):
        return reverse('management:companies')


class CompaniesUpdateView(base.CompanyUserRequiredMixin,
                          CompaniesBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', self.object)
        ]
        data = super(CompaniesUpdateView, self) \
            .get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs

        data['person_add_url'] = reverse('person_add', kwargs=self.kwargs)
        data['comment_add_url'] = reverse('comment_add', kwargs=self.kwargs)
        data['comment_delete_route'] = 'comment_delete'
        data['person_route'] = 'person'
        data['management'] = False

        return data

    def get_edit_url(self):
        return reverse('company_update', kwargs=self.kwargs)

    def get_back_url(self):
        return reverse('home')


class CompanyBaseEdit(base.ModelTableViewMixin,
                      SuccessMessageMixin,
                      generic.UpdateView):

    template_name = 'bdr_management/company_edit.html'
    model = Company
    success_message = _('Company edited successfully')
    form_class = CompanyForm

    def get_context_data(self, **kwargs):
        data = super(CompanyBaseEdit, self).get_context_data(**kwargs)

        return data

    def post(self, request, *args, **kwargs):
        curr_year = django_settings.get('Reporting year')
        reporting_years = ReportingYear.objects.filter(
            year__gte=settings.FIRST_REPORTING_YEAR).filter(year__lte=curr_year)
        for year in reporting_years:
            reported = bool(request.POST.get(unicode(year.year)))
            company = Company.objects.get(pk=kwargs['pk'])
            reporting_status, created = ReportingStatus.objects.get_or_create(
                company=company,
                reporting_year=year,
                defaults={'reported': reported})

            if not created:
                reporting_status.reported = reported
                reporting_status.save()

        return super(CompanyBaseEdit, self).post(request, *args, **kwargs)


class CompaniesManagementEdit(views.GroupRequiredMixin,
                              CompanyBaseEdit):

    group_required = settings.BDR_HELPDESK_GROUP

    def set_reporting_years(self, data):
        curr_year = django_settings.get('Reporting year')
        years = ReportingYear.objects.filter(
            year__gte=settings.FIRST_REPORTING_YEAR).filter(year__lte=curr_year)
        years_dict = {}
        company = self.object
        for year in years:
            status, _ = ReportingStatus.objects.get_or_create(
                company=company,
                reporting_year=year,
                defaults={'reported': False}
            )
            years_dict[unicode(year.year)] = status.reported
        data['years'] = years_dict

    def get_back_url(self):
        return reverse('management:companies_view',
                       kwargs={'pk': self.object.pk})

    def set_breadcrumbs(self, data):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:companies'),
                       _('Companies')),
            Breadcrumb(self.get_back_url(), self.object),
            Breadcrumb('', _(u'Edit %s' % self.object))
        ]
        data['breadcrumbs'] = breadcrumbs

    def get_context_data(self, **kwargs):
        data = super(CompaniesManagementEdit, self).get_context_data(**kwargs)
        data['management'] = True
        data['cancel_url'] = self.get_back_url()
        self.set_breadcrumbs(data)
        self.set_reporting_years(data)
        return data

    def get_success_url(self):
        return reverse('management:companies_view', kwargs=self.kwargs)


class CompaniesUpdate(base.CompanyUserRequiredMixin,
                      CompanyBaseEdit):

    def get_context_data(self, **kwargs):
        back_url = reverse('company', kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), _('Registry')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _(u'Edit %s' % self.object))
        ]
        data = super(CompaniesUpdate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data

    def get_form(self, form_class):
        form = super(CompaniesUpdate, self).get_form(form_class)
        form.fields.pop('name')
        return form

    def get_success_url(self):
        return reverse('company', kwargs=self.kwargs)


class CompanyDelete(views.GroupRequiredMixin,
                    base.ModelTableEditMixin,
                    generic.DeleteView):

    group_required = settings.BDR_HELPDESK_GROUP
    model = Company
    success_url = reverse_lazy('management:companies')
    template_name = 'bdr_management/company_confirm_delete.html'

    def get_context_data(self, **kwargs):
        back_url = reverse('management:companies_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:companies'),
                       _('Companies')),
            Breadcrumb(back_url,
                       self.object),
            Breadcrumb('', _('Delete company'))
        ]
        context = super(CompanyDelete, self).get_context_data(**kwargs)
        context['breadcrumbs'] = breadcrumbs
        context['form'] = CompanyDeleteForm()
        context['cancel_url'] = back_url
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Company deleted'))
        return super(CompanyDelete, self).delete(request, *args, **kwargs)


class CompanyAdd(views.GroupRequiredMixin,
                 SuccessMessageMixin,
                 generic.CreateView):

    group_required = settings.BDR_HELPDESK_GROUP

    template_name = 'bdr_management/company_add.html'
    model = Company
    form_class = CompanyForm
    success_message = _('Company created successfully')

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_to_response(
            self.get_context_data(form=self.get_form(self.get_form_class()),
                                  person_form=PersonFormWithoutCompany(),
                                  company_form=CompanyForm()))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        person_form = PersonFormWithoutCompany(self.request.POST)
        if form.is_valid() and person_form.is_valid():
            return self.form_valid(form, person_form)
        else:
            return self.form_invalid(form, person_form)

    def form_invalid(self, form, person_form):
        return self.render_to_response(
            self.get_context_data(form=self.get_form(self.get_form_class()),
                                  person_form=person_form))

    def form_valid(self, form, person_form):
        self.object = form.save()
        person_form.initial['company'] = self.object
        person_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('management:companies')

    def get_context_data(self, **kwargs):
        back_url = reverse('management:companies')
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(back_url, _('Companies')),
            Breadcrumb('', _('Add company'))
        ]
        context = super(CompanyAdd, self).get_context_data(**kwargs)
        context['breadcrumbs'] = breadcrumbs
        context['title'] = 'Add a new company'
        context['cancel_url'] = back_url
        return context


class ResetPassword(views.GroupRequiredMixin,
                    generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP

    template_name = 'bdr_management/reset_password.html'
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not self.company.account:
            raise Http404
        return super(ResetPassword, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        self.company.account.set_random_password()
        backend.sync_accounts_with_ldap([self.company.account])
        msg = _('Password has been reset.')
        messages.success(request, msg)

        if request.POST.get('perform_send'):
            n = backend.send_password_email_to_people(self.company)
            messages.success(
                request,
                'Emails have been sent to %d person(s).' % n
            )
        return redirect('management:companies_view',
                        pk=self.company.pk)


class CreateAccount(views.GroupRequiredMixin,
                    generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP

    template_name = 'bdr_management/create_account.html'
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if self.company.account:
            raise Http404
        return super(CreateAccount, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        obligation = self.company.obligation
        account = Account.objects.create_for_obligation(obligation)
        account.set_random_password()
        self.company.account = account
        self.company.save()
        backend.sync_accounts_with_ldap([account])
        msg = "Account created."
        messages.success(request, msg)

        if request.POST.get('perform_send'):
            n = backend.send_password_email_to_people(self.company)
            messages.success(
                request,
                'Emails have been sent to %d person(s).' % n
            )
        return redirect('management:companies_view',
                        pk=self.company.pk)


class CreateReportingFolder(views.GroupRequiredMixin,
                            generic.DetailView):

    API_ERROR_MSG = 'BDR_API_URL and BDR_API_AUTH not configured'

    group_required = settings.BDR_HELPDESK_GROUP

    template_name = 'bdr_management/create_reporting_folder.html'
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not (settings.BDR_API_URL and settings.BDR_API_AUTH):
            messages.error(request, self.API_ERROR_MSG)
            return redirect('management:companies_view',
                            pk=self.company.pk)
        return super(CreateReportingFolder, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        url = settings.BDR_API_URL + '/create_organisation_folder'
        form = {
            'country_code': self.company.country.code,
            'obligation_folder_name': self.company.obligation.reportek_slug,
            'account_uid': self.company.account.uid,
            'organisation_name': self.company.name,
        }
        resp = requests.post(url, data=form, auth=settings.BDR_API_AUTH)

        if resp.status_code != 200:
            messages.error(request, "BDR API request failed: %s" % resp)
        else:
            rv = resp.json()
            success = rv['success']
            if success:
                if rv['created']:
                    messages.success(request, "Created: %s" % rv['path'])
                else:
                    messages.warning(request, "Existing: %s" % rv['path'])
            else:
                messages.error(request, "Error: %s" % rv['error'])

        return redirect('management:companies_view',
                        pk=self.company.pk)


class CompaniesExport(views.StaffuserRequiredMixin,
                      generic.View):

    def get(self, request):
        header = ['userid', 'name', 'date_registered', 'active',
                  'addr_street', 'addr_place1', 'addr_postalcode',
                  'addr_place2', 'country', 'vat_number', 'obligation']
        rows = []
        for company in Company.objects.all():
            account = company.account
            rows.append([v.encode('utf-8') for v in [
                '' if account is None else account.uid,
                company.name,
                company.date_registered.strftime('%Y-%m-%d %H:%M:%S'),
                'on' if company.active else '',
                company.addr_street,
                company.addr_place1,
                company.addr_postalcode,
                company.addr_place2,
                company.country.name,
                company.vat_number or '',
                company.obligation.code if company.obligation else '',
            ]])

        xls_doc = backend.generate_excel(header, rows)
        return HttpResponse(xls_doc, content_type="application/vnd.ms-excel")


class CompanyNameHistory(views.StaffuserRequiredMixin,
                         generic.DetailView):

    template_name = 'bdr_management/company_name_history.html'
    model = Company

    def get_context_data(self, **kwargs):
        company = kwargs['object']
        back_url = reverse('management:companies_view',
                           kwargs={'pk': company.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:companies'),
                       _('Companies')),
            Breadcrumb(back_url, kwargs['object']),
            Breadcrumb('', _('Name history'))
        ]
        context = super(CompanyNameHistory, self).get_context_data()
        context['breadcrumbs'] = breadcrumbs

        return context
