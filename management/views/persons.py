from django.views.generic import (TemplateView, DetailView,
                                  UpdateView, DeleteView)
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from braces.views import (LoginRequiredMixin, StaffuserRequiredMixin,
                          GroupRequiredMixin)

from bdr_registry.models import Person
from management.base import FilterView, ModelTableViewMixin, ModelTableEditMixin


class Persons(LoginRequiredMixin,
              StaffuserRequiredMixin,
              TemplateView):

    template_name = 'persons.html'


class PersonsFilter(LoginRequiredMixin,
                    StaffuserRequiredMixin,
                    FilterView):

    def process_name(self, obj, val):
        url = reverse('management:persons_view',
                      kwargs={'pk': obj.pk})

        name = obj.first_name + ' ' + obj.family_name
        name = name.strip()

        if name:
            result = '<a href="%s">%s</a>' % (url, name)
        else:
            result = '<a href="%s"><i>Unknown Name</i></a>' % url

        return result

    def get_queryset(self, opt):
        queryset = Person.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(
                opt['order_by'].replace('name', 'family_name'))

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
                  ModelTableViewMixin,
                  DetailView):

    model = Person
    exclude = ('id', )
    back_url = reverse_lazy('management:persons')

    def dispatch(self, request, pk):
        self.edit_url = reverse('management:persons_edit',
                                kwargs={'pk': pk})
        self.delete_url = reverse('management:persons_delete',
                                  kwargs={'pk': pk})
        return super(PersonsView, self).dispatch(request, pk)


class PersonEdit(LoginRequiredMixin,
                 GroupRequiredMixin,
                 ModelTableEditMixin,
                 UpdateView):

    group_required = 'BDR helpdesk'
    model = Person

    def get_success_url(self):
        return reverse('management:persons_edit', kwargs=self.kwargs)


class PersonDelete(LoginRequiredMixin,
                   GroupRequiredMixin,
                   ModelTableEditMixin,
                   DeleteView):

    group_required = 'BDR helpdesk'
    model = Person
    success_url = reverse_lazy('management:persons')
