from django.views.generic import TemplateView
from django.db.models import Q
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

from bdr_registry.models import Person
from management.base import FilterView, ModelTableView


class Persons(LoginRequiredMixin, StaffuserRequiredMixin, TemplateView):

    template_name = 'persons.html'


class PersonsFilter(LoginRequiredMixin, StaffuserRequiredMixin, FilterView):

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


class PersonView(LoginRequiredMixin, StaffuserRequiredMixin, ModelTableView):

    model = Person
