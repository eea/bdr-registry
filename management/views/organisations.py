from django.views.generic import TemplateView, DetailView
from django.core.urlresolvers import reverse
from django.db.models import Q
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

from bdr_registry.models import Organisation
from management.forms.organisation_filters import OrganisationFilters
from management.base import FilterView, ModelTableMixin


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

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]


class OrganisationsView(LoginRequiredMixin,
                        StaffuserRequiredMixin,
                        ModelTableMixin,
                        DetailView):

    model = Organisation
    exclude = ('id', )
