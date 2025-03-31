from braces.views import GroupRequiredMixin

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views import generic

from bdr_management import base, forms
from bdr_management.base import Breadcrumb

from bdr_registry.models import Company, Comment


class CommentCreateBase(SuccessMessageMixin, generic.CreateView):

    template_name = "bdr_management/comment_edit.html"
    form_class = forms.CommentForm
    model = Comment
    success_message = _("Comment added successfully")

    def dispatch(self, *args, **kwargs):
        self.company = get_object_or_404(Company, **self.kwargs)
        return super(CommentCreateBase, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(CommentCreateBase, self).get_form_kwargs(**kwargs)
        data["initial"]["company"] = self.company
        return data

    def get_context_data(self, **kwargs):
        context = super(CommentCreateBase, self).get_context_data(**kwargs)
        context["title"] = "Add a new comment"
        context["object"] = self.company
        return context


class CommentManagementCreate(GroupRequiredMixin, CommentCreateBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = self.get_success_url()
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(back_url, self.company),
            Breadcrumb("", _("Add comment")),
        ]
        data = super(CommentManagementCreate, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_success_url(self):
        return reverse("management:companies_view", kwargs=self.kwargs)


class CommentCreate(
    base.CompanyUserRequiredMixin, GroupRequiredMixin, CommentCreateBase
):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = self.get_success_url()
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(back_url, self.company),
            Breadcrumb("", _("Add comment")),
        ]
        data = super(CommentCreate, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_success_url(self):
        return reverse("company", kwargs=self.kwargs)


class CommentDeleteBase(generic.DeleteView):

    pk_url_kwarg = "comment_pk"
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        self.company = get_object_or_404(Company, pk=self.kwargs["pk"])
        return super(CommentDeleteBase, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Comment deleted"))
        return super(CommentDeleteBase, self).delete(request, *args, **kwargs)


class CommentManagementDelete(GroupRequiredMixin, CommentDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_success_url(self):
        return reverse("management:companies_view", kwargs={"pk": self.company.pk})


class CommentDelete(base.CompanyUserRequiredMixin, CommentDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_success_url(self):
        return reverse("company", kwargs={"pk": self.company.pk})
