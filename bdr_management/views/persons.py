from braces import views

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views import generic

from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_management.forms import PersonFormWithoutCompany, PersonForm
from bdr_management.views.mixins import CompanyMixin

from bdr_registry.models import Company, Person, User
from bdr_registry.utils import set_role_for_account


class Persons(views.StaffuserRequiredMixin, generic.TemplateView):

    template_name = "bdr_management/persons.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Persons")),
        ]
        data = super(Persons, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        return data


class PersonsFilter(views.StaffuserRequiredMixin, CompanyMixin, base.FilterView):

    raise_exception = True

    def process_name(self, obj, val):
        url = reverse("management:persons_view", kwargs={"pk": obj.pk})

        name = obj.first_name + " " + obj.family_name
        name = name.strip()

        if name:
            result = '<a href="%s">%s</a>' % (url, name)
        else:
            result = '<a href="%s"><i>Unknown Name</i></a>' % url

        return result

    def get_queryset(self, opt):

        user_obligations = self.get_obligations()

        queryset = Person.objects.filter(
            company__obligation__id__in=user_obligations
        ).all()

        if "order_by" in opt and opt["order_by"]:
            queryset = queryset.order_by(opt["order_by"].replace("name", "family_name"))

        if "search" in opt and opt["search"]:
            search_filters = (
                Q(first_name__icontains=opt["search"])
                | Q(family_name__icontains=opt["search"])
                | Q(email__icontains=opt["search"])
            )
            queryset = queryset.filter(search_filters)

        if opt["count"]:
            return queryset.count()

        return queryset[opt["offset"] : opt["limit"]]


class PersonBaseView(base.ModelTableViewMixin, generic.DetailView):

    template_name = "bdr_management/person_view.html"
    model = Person
    exclude = ("id",)

    def get_context_data(self, **kwargs):
        context = super(PersonBaseView, self).get_context_data(**kwargs)
        company = self.object.company
        folder_path = company.build_reporting_folder_path()
        context["has_reporting_folder"] = company.has_reporting_folder(folder_path)
        return context


class PersonManagementView(views.StaffuserRequiredMixin, PersonBaseView):

    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:persons"), _("Persons")),
            Breadcrumb("", self.object),
        ]
        data = super(PersonManagementView, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["management"] = True
        return data

    def get_edit_url(self):
        return reverse("management:persons_edit", kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse("management:persons_delete", kwargs=self.kwargs)

    def get_back_url(self):
        return reverse("management:persons")


class PersonFromCompanyView(PersonManagementView):
    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(
                reverse("management:companies_view", kwargs={"pk": self.kwargs["cpk"]}),
                self.object.company,
            ),
            Breadcrumb("", self.object),
        ]
        data = super(PersonFromCompanyView, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        return data

    def get_edit_url(self):
        return reverse("management:person_from_company_edit", kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse("management:person_from_company_delete", kwargs=self.kwargs)

    def get_back_url(self):
        return reverse("management:companies_view", kwargs={"pk": self.kwargs["cpk"]})


class PersonView(base.PersonUserRequiredMixin, PersonBaseView):

    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", self.object),
        ]
        data = super(PersonView, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["management"] = False
        return data

    def get_back_url(self):
        return reverse("company", kwargs={"pk": self.object.company.id})

    def get_edit_url(self):
        return reverse("person_update", kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse("person_delete", kwargs=self.kwargs)


class PersonEditBase(base.ModelTableViewMixin, SuccessMessageMixin, generic.UpdateView):

    template_name = "bdr_management/person_edit.html"
    model = Person
    success_message = _("Person edited successfully")
    form_class = PersonForm

    def post(self, request, *args, **kwargs):
        person = self.get_object()
        company = person.company
        response = super(PersonEditBase, self).post(request, *args, **kwargs)
        company_updated = self.get_object().company
        if company != company_updated and person.account:
            set_role_for_account(company, person.account.uid, "remove")
            set_role_for_account(company_updated, person.account.uid, "add")
        return response


class PersonManagementEdit(views.GroupRequiredMixin, PersonEditBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse("management:persons_view", kwargs={"pk": self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:persons"), _("Persons")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _("Edit %s" % self.object)),
        ]
        data = super(PersonManagementEdit, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_success_url(self):
        return reverse("management:persons_view", kwargs=self.kwargs)


class PersonFromCompanyEdit(PersonManagementEdit):
    def get_context_data(self, **kwargs):
        data = super(PersonFromCompanyEdit, self).get_context_data(**kwargs)
        data["cancel_url"] = reverse(
            "management:person_from_company", kwargs=self.kwargs
        )
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(
                reverse("management:companies_view", kwargs={"pk": self.kwargs["cpk"]}),
                self.object.company,
            ),
            Breadcrumb(data["cancel_url"], self.object),
            Breadcrumb("", _("Edit %s" % self.object)),
        ]
        data["breadcrumbs"] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse("management:person_from_company", kwargs=self.kwargs)


class PersonEdit(base.PersonUserRequiredMixin, PersonEditBase):

    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse("person", kwargs={"pk": self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse("home"), _("Registry")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _("Edit %s" % self.object)),
        ]
        data = super(PersonEdit, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_success_url(self):
        return reverse("person", kwargs=self.kwargs)


class PersonDeleteBase(base.ModelTableEditMixin, generic.DeleteView):

    model = Person
    template_name = "bdr_management/person_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        if self.company_has_other_reporters():
            messages.success(request, _("Person deleted"))
            response = super(PersonDeleteBase, self).delete(request, *args, **kwargs)
            if self.object.account:
                user = User.objects.filter(username=self.object.account.uid)
                if user:
                    user = user.first()
                    user.is_active = False
                    user.save()
                set_role_for_account(
                    self.object.company, self.object.account.uid, "remove"
                )
            return response
        else:
            return self.cannot_delete_last_reporter()

    def get(self, request, *args, **kwargs):
        if self.company_has_other_reporters():
            return super(PersonDeleteBase, self).get(request, *args, **kwargs)
        else:
            return self.cannot_delete_last_reporter()

    def cannot_delete_last_reporter(self):
        messages.error(
            self.request,
            _(
                "Cannot delete the only designated company reporter "
                'for "%s"' % self.get_object().company
            ),
        )
        return HttpResponseRedirect(self.get_view_url())

    def company_has_other_reporters(self):
        return self.get_object().company.people.count() > 1

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = super(PersonDeleteBase, self).get_object()
        return self.object


class PersonManagementDelete(views.GroupRequiredMixin, PersonDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP
    success_url = reverse_lazy("management:persons")
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = self.get_view_url()
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:persons"), _("Persons")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _("Delete %s" % self.object)),
        ]
        data = super(PersonManagementDelete, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_view_url(self):
        return reverse("management:persons_view", kwargs={"pk": self.get_object().pk})


class PersonFromCompanyDelete(PersonManagementDelete):
    def get_context_data(self, **kwargs):
        data = super(PersonFromCompanyDelete, self).get_context_data(**kwargs)
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(
                reverse("management:companies_view", kwargs={"pk": self.kwargs["cpk"]}),
                self.object.company,
            ),
            Breadcrumb(data["cancel_url"], self.object),
            Breadcrumb("", _("Delete %s" % self.object)),
        ]
        data["breadcrumbs"] = breadcrumbs
        return data

    def get_success_url(self):
        return reverse("management:companies_view", kwargs={"pk": self.kwargs["cpk"]})

    def get_view_url(self):
        return reverse("management:person_from_company", kwargs=self.kwargs)


class PersonDelete(base.PersonUserRequiredMixin, PersonDeleteBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_success_url(self):
        return reverse("company", kwargs={"pk": self.company.pk})

    def get_context_data(self, **kwargs):
        back_url = self.get_view_url()
        breadcrumbs = [
            Breadcrumb(reverse("home"), _("Registry")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _("Delete %s" % self.object)),
        ]
        data = super(PersonDelete, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data

    def get_view_url(self):
        return reverse("person", kwargs={"pk": self.get_object().pk})


class PersonCreateBase(SuccessMessageMixin, generic.CreateView):

    template_name = "bdr_management/person_add.html"
    model = Person
    form_class = PersonFormWithoutCompany
    success_message = _("Person created successfully")

    def dispatch(self, *args, **kwargs):
        self.company = get_object_or_404(Company, **self.kwargs)
        return super(PersonCreateBase, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        data = super(PersonCreateBase, self).get_form_kwargs(**kwargs)
        data["initial"]["company"] = self.company
        return data

    def get_context_data(self, **kwargs):
        context = super(PersonCreateBase, self).get_context_data(**kwargs)
        context["title"] = "Add a new person"
        context["object"] = self.company
        return context


class PersonManagementCreate(views.GroupRequiredMixin, PersonCreateBase):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def get_success_url(self):
        return reverse("management:companies_view", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse("management:companies_view", kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(back_url, self.company),
            Breadcrumb("", _("Add comment")),
        ]
        data = super(PersonManagementCreate, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data


class PersonCreate(base.CompanyUserRequiredMixin, PersonCreateBase):

    raise_exception = True

    def get_success_url(self):
        return reverse("company", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        back_url = reverse("company", kwargs=self.kwargs)
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(back_url, self.company),
            Breadcrumb("", _("Add person")),
        ]
        data = super(PersonCreate, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        return data
