from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from braces import views

from bdr_registry.models import Person, Organisation
from bdr_management import base
from bdr_management.forms import PersonForm


class Persons(views.StaffuserRequiredMixin,
              generic.TemplateView):

    template_name = 'bdr_management/persons.html'


class PersonsFilter(views.StaffuserRequiredMixin,
                    base.FilterView):

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


class PersonsBaseView(base.ModelTableViewMixin,
                      generic.DetailView):

    template_name = 'bdr_management/person_view.html'
    model = Person
    exclude = ('id', )

    def get_delete_url(self):
        return reverse('management:persons_delete', kwargs=self.kwargs)


class PersonsManagementView(views.StaffuserRequiredMixin,
                            PersonsBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            base.Breadcrumb(reverse('home'), title=_('Registry')),
            base.Breadcrumb(reverse('management:persons'),
                            _('Persons')),
            base.Breadcrumb('', self.object)
        ]
        data = super(PersonsManagementView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('management:persons_edit', kwargs=self.kwargs)


class PersonsUpdateView(base.OrganisationUserRequiredMixin,
                        PersonsBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            base.Breadcrumb(reverse('home'), title=_('Registry')),
            base.Breadcrumb('', self.object)
        ]
        data = super(PersonsUpdateView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('person_update', kwargs=self.kwargs)


class PersonBaseEdit(base.ModelTableViewMixin,
                     SuccessMessageMixin,
                     generic.UpdateView):

    template_name = 'bdr_management/person_edit.html'
    model = Person
    success_message = _('Person edited successfully')


class PersonsManagementEdit(views.GroupRequiredMixin,
                            PersonBaseEdit):

    group_required = 'BDR helpdesk'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            base.Breadcrumb(reverse('home'), title=_('Registry')),
            base.Breadcrumb(reverse('management:persons'),
                            _('Persons')),
            base.Breadcrumb(reverse('management:persons_view',
                            kwargs={'pk': self.object.pk}),
                            self.object),
            base.Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(PersonsManagementEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse('management:persons_view', kwargs=self.kwargs)


class PersonsUpdate(base.OrganisationUserRequiredMixin,
                    PersonsBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            base.Breadcrumb(reverse('home'), _('Registry')),
            base.Breadcrumb(reverse('person', kwargs={'pk': self.object.pk}),
                            self.object),
            base.Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(PersonsUpdate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse('person', kwargs=self.kwargs)


class PersonDelete(views.GroupRequiredMixin,
                   base.ModelTableEditMixin,
                   generic.DeleteView):

    group_required = 'BDR helpdesk'
    model = Person
    success_url = reverse_lazy('management:persons')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Person deleted"))
        return super(PersonDelete, self).delete(request, *args, **kwargs)


class PersonAdd(views.GroupRequiredMixin,
                SuccessMessageMixin,
                generic.CreateView):

    template_name = 'bdr_management/person_add.html'
    group_required = 'BDR helpdesk'
    model = Person
    form_class = PersonForm
    success_message = _('Person created successfully')

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(Organisation, **self.kwargs)
        return super(PersonAdd, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(PersonAdd, self).get_form_kwargs(**kwargs)
        data['initial']['organisation'] = self.organisation
        return data

    def get_context_data(self, **kwargs):
        context = super(PersonAdd, self).get_context_data(**kwargs)
        context['title'] = 'Add a new person'
        context['object'] = self.organisation
        return context
