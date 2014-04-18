from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views import generic

from braces import views

from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_management.forms import PersonForm
from bdr_registry.models import Person, Organisation


class Persons(views.StaffuserRequiredMixin,
              generic.TemplateView):

    template_name = 'bdr_management/persons.html'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Persons')),
        ]
        data = super(Persons, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


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


class PersonBaseView(base.ModelTableViewMixin,
                     generic.DetailView):

    template_name = 'bdr_management/person_view.html'
    model = Person
    exclude = ('id', )


class PersonManagementView(views.StaffuserRequiredMixin,
                           PersonBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:persons'),
                       _('Persons')),
            Breadcrumb('', self.object)
        ]
        data = super(PersonManagementView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('management:persons_edit', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('management:persons_delete', kwargs=self.kwargs)


class PersonView(base.PersonUserRequiredMixin,
                 PersonBaseView):

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', self.object)
        ]
        data = super(PersonView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('person_update', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('person_delete', kwargs=self.kwargs)


class PersonEditBase(base.ModelTableViewMixin,
                       SuccessMessageMixin,
                       generic.UpdateView):

    template_name = 'bdr_management/person_edit.html'
    model = Person
    success_message = _('Person edited successfully')


class PersonManagementEdit(views.GroupRequiredMixin,
                             PersonEditBase):

    group_required = settings.BDR_HELPDESK_GROUP

    def get_context_data(self, **kwargs):
        back_url = reverse('management:persons_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:persons'),
                       _('Persons')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(PersonManagementEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data

    def get_success_url(self):
        return reverse('management:persons_view', kwargs=self.kwargs)


class PersonEdit(base.PersonUserRequiredMixin,
                 PersonEditBase):

    fields = ('title', 'family_name', 'first_name', 'email', 'phone',
              'phone2', 'phone3', 'fax')

    def get_context_data(self, **kwargs):
        back_url = reverse('person', kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), _('Registry')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _('Edit %s' % self.object))
        ]
        data = super(PersonEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data

    def get_success_url(self):
        return reverse('person', kwargs=self.kwargs)


class PersonDeleteBase(base.ModelTableEditMixin,
                       generic.DeleteView):

    model = Person
    template_name = 'bdr_management/person_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Person deleted"))
        return super(PersonDeleteBase, self).delete(request, *args, **kwargs)


class PersonManagementDelete(views.GroupRequiredMixin,
                             PersonDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP
    success_url = reverse_lazy('management:persons')


class PersonDelete(base.PersonUserRequiredMixin,
                   PersonDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP

    def get_success_url(self):
        return reverse('organisation', kwargs={'pk': self.organisation.pk})


class PersonCreateBase(SuccessMessageMixin,
                       generic.CreateView):

    template_name = 'bdr_management/person_add.html'
    model = Person
    form_class = PersonForm
    success_message = _('Person created successfully')

    def dispatch(self, *args, **kwargs):
        self.organisation = get_object_or_404(Organisation, **self.kwargs)
        return super(PersonCreateBase, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(PersonCreateBase, self).get_form_kwargs(**kwargs)
        data['initial']['organisation'] = self.organisation
        return data

    def get_context_data(self, **kwargs):
        context = super(PersonCreateBase, self).get_context_data(**kwargs)
        context['title'] = 'Add a new person'
        context['object'] = self.organisation
        return context


class PersonManagementCreate(views.GroupRequiredMixin,
                             PersonCreateBase):

    group_required = settings.BDR_HELPDESK_GROUP

    def get_success_url(self):
        return reverse('management:organisations_view', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse('management:organisations_view', kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:organisations'), _('Organisations')),
            Breadcrumb(back_url, self.organisation),
            Breadcrumb('', _('Add comment'))
        ]
        data = super(PersonManagementCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data


class PersonCreate(base.OrganisationUserRequiredMixin,
                   PersonCreateBase):

    def get_success_url(self):
        return reverse('organisation', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse('organisation', kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(back_url,
                       self.organisation),
            Breadcrumb('', _('Add person'))
        ]
        data = super(PersonCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data
