from datetime import date, timedelta

from bdr_management.base import Breadcrumb, OrganisationUserRequiredMixin
from bdr_management.forms.organisations import OrganisationForm
from braces.views import SuperuserRequiredMixin
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from braces import views
from bdr_registry.models import Organisation
from bdr_management import base, forms


class Organisations(views.StaffuserRequiredMixin,
                    generic.TemplateView):

    template_name = 'bdr_management/organisations.html'

    def get_context_data(self, **kwargs):
        context = super(Organisations, self).get_context_data(**kwargs)
        context['form'] = forms.OrganisationFilters()
        return context


class OrganisationsFilter(views.StaffuserRequiredMixin,
                          base.FilterView):

    def process_name(self, object, val):
        url = reverse('management:organisations_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def process_date_registered(self, object, val):
        return val.strftime(settings.DATE_FORMAT)

    def get_queryset(self, opt):
        queryset = Organisation.objects.all()

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
            if filters['account'] == forms.OrganisationFilters.WITHOUT_ACCOUNT:
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
        if selected_option == forms.OrganisationFilters.TODAY:
            start_date = today
        elif selected_option == forms.OrganisationFilters.LAST_7_DAYS:
            start_date = today - timedelta(days=7)
        elif selected_option == forms.OrganisationFilters.THIS_MONTH:
            start_date = date(today.year, today.month, 1)
        else:
            start_date = date(today.year, 1, 1)
        return start_date


class OrganisationsBaseView(base.ModelTableViewMixin,
                            generic.DetailView):

    template_name = 'bdr_management/organisation_view.html'
    model = Organisation
    exclude = ('id', )

    def get_delete_url(self):
        return reverse('management:organisations_delete', kwargs=self.kwargs)


class OrganisationsManagementView(views.StaffuserRequiredMixin,
                                  OrganisationsBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:organisations'),
                       _('Organisations')),
            Breadcrumb('', self.object)
        ]
        data = super(OrganisationsManagementView, self) \
            .get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('management:organisations_edit', kwargs=self.kwargs)


class OrganisationsUpdateView(OrganisationUserRequiredMixin,
                              OrganisationsBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', self.object)
        ]
        data = super(OrganisationsUpdateView, self) \
            .get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('organisation_update', kwargs=self.kwargs)


class OragnisationBaseEdit(base.ModelTableViewMixin,
                           SuccessMessageMixin,
                           generic.UpdateView):

    template_name = 'bdr_management/organisation_edit.html'
    model = Organisation
    success_message = _('Organisation edited successfully')


class OrganisationsManagementEdit(views.GroupRequiredMixin,
                                  OragnisationBaseEdit):

    group_required = 'BDR helpdesk'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:organisations'), _('Organisations')),
            Breadcrumb(reverse('management:organisations_view',
                               kwargs={'pk': self.object.pk}),
                       self.object),
            Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(OrganisationsManagementEdit, self) \
            .get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)


class OrganisationsUpdate(OrganisationUserRequiredMixin,
                          OragnisationBaseEdit):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), _('Registry')),
            Breadcrumb(reverse('organisation',
                               kwargs={'pk': self.object.pk}),
                       self.object),
            Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(OrganisationsUpdate, self) \
            .get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse('organisation', kwargs=self.kwargs)


class OrganisationDelete(views.GroupRequiredMixin,
                         base.ModelTableEditMixin,
                         generic.DeleteView):

    group_required = 'BDR helpdesk'
    model = Organisation
    success_url = reverse_lazy('management:organisations')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Organisation deleted'))
        return super(OrganisationDelete, self).delete(request, *args, **kwargs)


class OrganisationAdd(SuperuserRequiredMixin,
                      SuccessMessageMixin,
                      generic.CreateView):

    template_name = 'bdr_management/organisation_add.html'
    model = Organisation
    form_class = OrganisationForm
    success_message = _('Organisation created successfully')

    def get_success_url(self):
        return reverse('management:organisations')

    def get_context_data(self, **kwargs):
        context = super(OrganisationAdd, self).get_context_data(**kwargs)
        context['title'] = 'Add a new organisation'
        return context
