from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views import generic

from post_office.models import EmailTemplate

from braces import views

from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_management.forms.email_template import EmailTemplateForm


class EmailTemplates(views.StaffuserRequiredMixin,
                     generic.TemplateView):

    template_name = 'bdr_management/email_templates.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Email templates')),
        ]
        data = super(EmailTemplates, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


class EmailTemplatesFilter(views.StaffuserRequiredMixin,
                           base.FilterView):

    raise_exception = True

    def process_name(self, object, val):
        url = reverse('management:email_template_view',
                      kwargs={'pk': object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def get_queryset(self, opt):

        user_templates = [
            obligation['email_template_id']
            for obligation in self.request.user.obligations.values()
        ]

        queryset = EmailTemplate.objects.filter(pk__in=user_templates).all()

        if 'order_by' in opt and opt['order_by']:
            queryset = queryset.order_by(opt['order_by'])

        if 'search' in opt and opt['search']:
            search_filters = (
                Q(name__icontains=opt['search']) |
                Q(subject__icontains=opt['search'])
            )
            queryset = queryset.filter(search_filters)

        if opt['count']:
            return queryset.count()

        return queryset[opt['offset']: opt['limit']]


class EmailTemplateView(views.StaffuserRequiredMixin,
                        base.ModelTableViewMixin,
                        generic.DetailView):

    template_name = 'bdr_management/email_template_view.html'
    model = EmailTemplate
    exclude = ('id', 'content', 'description')
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:email_templates'),
                       _('Email templates')),
            Breadcrumb('', self.object)
        ]
        data = super(EmailTemplateView, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['management'] = True
        return data

    def get_edit_url(self):
        return reverse('management:email_template_edit', kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse('management:email_template_delete', kwargs=self.kwargs)

    def get_back_url(self):
        return reverse('management:email_templates')


class EmailTemplateEdit(views.GroupRequiredMixin,
                        base.ModelTableViewMixin,
                        SuccessMessageMixin,
                        generic.UpdateView):

    template_name = 'bdr_management/email_template_edit.html'
    model = EmailTemplate
    success_message = _('Template edited successfully')
    group_required = settings.BDR_HELPDESK_GROUP
    form_class = EmailTemplateForm
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse('management:email_template_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:email_templates'),
                       _('Email templates')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _(u'Edit %s' % self.object))
        ]
        data = super(EmailTemplateEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data

    def get_success_url(self):
        return reverse('management:email_template_view', kwargs=self.kwargs)


class EmailTemplateDelete(views.GroupRequiredMixin,
                          base.ModelTableEditMixin,
                          generic.DeleteView):

    model = EmailTemplate
    template_name = 'bdr_management/email_template_confirm_delete.html'
    group_required = settings.BDR_HELPDESK_GROUP
    success_url = reverse_lazy('management:email_templates')
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse('management:email_template_view',
                           kwargs={'pk': self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(reverse('management:email_templates'),
                       _('Email templates')),
            Breadcrumb(back_url, self.object),
            Breadcrumb('', _(u'Delete %s' % self.object))
        ]
        data = super(EmailTemplateDelete, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data


class EmailTemplateCreate(views.GroupRequiredMixin,
                          SuccessMessageMixin,
                          generic.CreateView):

    model = EmailTemplate
    form_class = EmailTemplateForm

    template_name = 'bdr_management/email_template_edit.html'
    success_message = _('Template created successfully')
    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_success_url(self):
        return reverse('management:email_templates', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse('management:email_templates', kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(back_url, _('Email templates')),
            Breadcrumb('', _('Create new template'))
        ]
        data = super(EmailTemplateCreate, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = back_url
        return data
