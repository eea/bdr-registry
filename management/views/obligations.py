from django.views.generic import TemplateView, DetailView
from django.core.urlresolvers import reverse
from django.db.models import Q
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

from bdr_registry.models import Obligation
from management.base import FilterView, ModelTableMixin


class Obligations(LoginRequiredMixin,
                  StaffuserRequiredMixin,
                  TemplateView):

    template_name = 'obligations.html'


class ObligationsFilter(LoginRequiredMixin,
                        StaffuserRequiredMixin,
                        FilterView):

    def process_name(self, object, val):
        url = reverse('management:obligations_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def get_queryset(self, opt):
        queryset = Obligation.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(name__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]


class ObligationsView(LoginRequiredMixin,
                      StaffuserRequiredMixin,
                      ModelTableMixin,
                      DetailView):

    model = Obligation
    exclude = ('id', )
