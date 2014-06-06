from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from braces import views
import django_settings

from bdr_management.base import Breadcrumb
from django_settings.models import Setting
from bdr_management.forms.settings_form import SettingsForm


class Settings(views.StaffuserRequiredMixin,
               generic.ListView):

    template_name = 'bdr_management/settings_view.html'
    queryset = Setting.objects.all()
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Settings')),
        ]
        data = super(Settings, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        return data


class SettingsEdit(views.GroupRequiredMixin,
                   generic.FormView):

    template_name = 'bdr_management/settings_edit.html'
    group_required = settings.BDR_HELPDESK_GROUP
    form_class = SettingsForm
    success_url = reverse_lazy('management:settings_view')
    raise_exception = True

    def get_initial(self):
        return {
            'reporting_year': django_settings.get('Reporting year')
        }

    def get_context_data(self, **kwargs):
        settings_url = reverse('management:settings_view')
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb(settings_url, _('Settings')),
            Breadcrumb('', _('Edit'))
        ]
        data = super(SettingsEdit, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = settings_url
        return data
