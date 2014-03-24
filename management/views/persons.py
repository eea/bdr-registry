from django.views.generic import TemplateView, DetailView
from django.core.urlresolvers import reverse
from django.db.models import Q
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

from bdr_registry.models import Person
from management.base import FilterView, ModelTableMixin


class Persons(LoginRequiredMixin,
              StaffuserRequiredMixin,
              TemplateView):

    template_name = 'persons.html'


class PersonsFilter(LoginRequiredMixin,
                    StaffuserRequiredMixin,
                    FilterView):

    @staticmethod
    def _process_column(obj, val):
        url = reverse('management:persons_view',
                      kwargs={'pk': obj.pk})
        return '<a href="%s">%s</a>' % (url, val)

    @staticmethod
    def process_first_name(obj, val):
        return PersonsFilter._process_column(obj, val)

    @staticmethod
    def process_family_name(obj, val):
        return PersonsFilter._process_column(obj, val)

    def get_queryset(self, opt):
        queryset = Person.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(first_name__icontains=opt['search']) |
                Q(family_name__icontains=opt['search']) |
                Q(email__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]


class PersonsView(LoginRequiredMixin,
                  StaffuserRequiredMixin,
                  ModelTableMixin,
                  DetailView):

    model = Person
    exclude = ('id', )
