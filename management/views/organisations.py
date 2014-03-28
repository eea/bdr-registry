from datetime import date, timedelta

from django.views.generic import (TemplateView, DetailView,
                                  UpdateView, DeleteView)
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from braces.views import (LoginRequiredMixin, StaffuserRequiredMixin,
                          GroupRequiredMixin)
from bdr_registry.models import Organisation
from management.forms.organisation_filters import OrganisationFilters
from management.base import FilterView, ModelTableViewMixin, ModelTableEditMixin


class Organisations(LoginRequiredMixin,
                    StaffuserRequiredMixin,
                    TemplateView):

    template_name = 'organisations.html'

    def get_context_data(self, **kwargs):
        context = super(Organisations, self).get_context_data(**kwargs)
        context['form'] = OrganisationFilters()
        return context


class OrganisationsFilter(LoginRequiredMixin,
                          StaffuserRequiredMixin,
                          FilterView):

    def process_name(self, object, val):
        url = reverse('management:organisations_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)



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
            if filters['account'] == OrganisationFilters.WITH_ACCOUNT:
                queryset = queryset.exclude(account__isnull=False)
            else:
                queryset = queryset.exclude(account__isnull=True)
        if 'date_registered' in filters:
            start_date = self._get_startdate(filters['date_registered'])
            queryset = queryset.exclude(date_registered__lt=start_date)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]

    @staticmethod
    def _get_startdate(selected_option):
        today = date.today()
        if selected_option == OrganisationFilters.TODAY:
            start_date = today
        elif selected_option == OrganisationFilters.LAST_7_DAYS:
            start_date = today - timedelta(days=7)
        elif selected_option == OrganisationFilters.THIS_MONTH:
            start_date = date(today.year, today.month, 1)
        else:
            start_date = date(today.year, 1, 1)
        return start_date


class OrganisationsView(LoginRequiredMixin,
                        StaffuserRequiredMixin,
                        ModelTableViewMixin,
                        DetailView):

    model = Organisation
    exclude = ('id', )
    back_url = reverse_lazy('management:organisations')

    def get_edit_url(self):
        return reverse('management:organisations_edit',
                       kwargs={'pk': self.kwargs['pk']})

    def get_delete_url(self):
        return reverse('management:organisations_delete',
                       kwargs={'pk': self.kwargs['pk']})


class OrganisationsEdit(LoginRequiredMixin,
                        GroupRequiredMixin,
                        ModelTableEditMixin,
                        UpdateView):

    group_required = 'BDR helpdesk'
    model = Organisation

    def get_success_url(self):
        return reverse('management:organisations_edit', kwargs=self.kwargs)


class OrganisationDelete(LoginRequiredMixin,
                         GroupRequiredMixin,
                         ModelTableEditMixin,
                         DeleteView):

    group_required = 'BDR helpdesk'
    model = Organisation
    success_url = reverse_lazy('management:organisations')
