from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q

from bdr_registry.models import Organisation
from management.base import FilterView


class Organisations(TemplateView):

    template_name = 'organisations.html'


class OrganisationsFilter(FilterView):

    def get_queryset(self, opt):
        queryset = Organisation.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = Q(name__icontains=opt['search'])
            queryset = queryset.filter(search_filters)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]
