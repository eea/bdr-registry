from braces import views

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from bdr_management.base import Breadcrumb
from bdr_management import base
from bdr_management.forms.settings_form import SettingsForm
from bdr_registry.models import SiteConfiguration


class Settings(
    views.StaffuserRequiredMixin, base.ModelTableViewMixin, generic.DetailView
):

    template_name = "bdr_management/settings_view.html"
    raise_exception = True
    model = SiteConfiguration
    exclude = ("id",)

    def get_object(self, queryset=None):
        return SiteConfiguration.objects.get()

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Settings")),
        ]
        data = super(Settings, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["management"] = True
        return data

    def get_edit_url(self):
        return reverse("management:settings_edit")

    def get_back_url(self):
        return reverse("home")


class SettingsEdit(views.GroupRequiredMixin, SuccessMessageMixin, generic.UpdateView):

    template_name = "bdr_management/settings_edit.html"
    group_required = settings.BDR_HELPDESK_GROUP
    form_class = SettingsForm
    success_url = reverse_lazy("management:settings_view")
    raise_exception = True
    success_message = _("Settings edited successfully")

    def get_object(self, queryset=None):
        return SiteConfiguration.objects.get()

    def get_context_data(self, **kwargs):
        settings_url = reverse("management:settings_view")
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(settings_url, _("Settings")),
            Breadcrumb("", _("Edit")),
        ]
        data = super(SettingsEdit, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = settings_url
        data["management"] = True
        return data
