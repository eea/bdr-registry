from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views import generic

from braces import views

from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_registry.models import Obligation


class Obligations(views.StaffuserRequiredMixin,
                  generic.TemplateView):

    template_name = 'bdr_management/obligations.html'

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Obligations')),
        ]
        data = super(Obligations, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


class ObligationsFilter(views.StaffuserRequiredMixin,
                        base.FilterView):

    def process_name(self, object, val):
        url = reverse('management:obligation_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def get_queryset(self, opt):
        queryset = Obligation.objects.all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(name__icontains=opt['search']) |
                Q(code__icontains=opt['search']) |
                Q(reportek_slug__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]


class ObligationView(views.StaffuserRequiredMixin,
                     base.ModelTableViewMixin,
                     generic.DetailView):

    template_name = 'bdr_management/obligation_view.html'
    model = Obligation
    exclude = ('id', )

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:obligations'),
                       _('Obligations')),
            Breadcrumb('', self.object)
        ]
        data = super(ObligationView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse('management:obligation_edit', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('management:obligation_delete', kwargs=self.kwargs)

    def get_back_url(self):
        return reverse('management:obligations')


class ObligationEdit(views.GroupRequiredMixin,
                     base.ModelTableViewMixin,
                     SuccessMessageMixin,
                     generic.UpdateView):

    template_name = 'bdr_management/obligation_edit.html'
    model = Obligation
    success_message = _('Obligation edited successfully')
    group_required = settings.BDR_HELPDESK_GROUP

    def get_context_data(self, **kwargs):
        back_url = reverse('management:obligation_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:obligations'),
                       _('Obligations')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _(u'Edit %s' % self.object))
        ]
        data = super(ObligationEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data

    def get_success_url(self):
        return reverse('management:obligation_view', kwargs=self.kwargs)


class ObligationDelete(views.GroupRequiredMixin,
                       base.ModelTableEditMixin,
                       generic.DeleteView):

    model = Obligation
    template_name = 'bdr_management/obligation_confirm_delete.html'
    group_required = settings.BDR_HELPDESK_GROUP
    success_url = reverse_lazy('management:obligations')

    def get_context_data(self, **kwargs):
        back_url = reverse('management:obligation_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:obligations'),
                       _('Obligations')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _(u'Delete %s' % self.object))
        ]
        data = super(ObligationDelete, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data


class ObligationCreate(views.GroupRequiredMixin,
                       SuccessMessageMixin,
                       generic.CreateView):

    template_name = 'bdr_management/obligation_add.html'
    model = Obligation
    success_message = _('Obligation created successfully')
    group_required = settings.BDR_HELPDESK_GROUP

    def get_success_url(self):
        return reverse('management:email_templates', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse('management:email_templates', kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(back_url, _('Email templates')),
            Breadcrumb('', _('Create new template'))
        ]
        data = super(ObligationCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data
