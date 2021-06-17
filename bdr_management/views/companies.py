from braces import views
from datetime import date, timedelta
import json
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views import generic

from bdr_management import base, forms, backend
from bdr_management.base import Breadcrumb, is_staff_user, ApiAccessMixin
from bdr_management.forms import PersonFormWithoutCompany
from bdr_management.forms.companies import CompanyForm, CompanyDeleteForm
from bdr_management.views.mixins import CompanyMixin
from bdr_management.views.password_set import SetPasswordMixin

from bdr_registry.admin import set_role_for_person_account
from bdr_registry.models import (
    Account,
    Company,
    Person,
    ReportingStatus,
    ReportingYear,
    SiteConfiguration,
    User,
)
from bdr_registry.views import CanEdit


class Companies(views.StaffuserRequiredMixin, CompanyMixin, generic.TemplateView):

    template_name = "bdr_management/companies.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Companies")),
        ]

        user_obligations = self.get_obligations()

        context = super(Companies, self).get_context_data(**kwargs)
        context["breadcrumbs"] = breadcrumbs
        context["form"] = forms.CompanyFilters(obligations=user_obligations)
        return context


class CompaniesFilter(views.StaffuserRequiredMixin, CompanyMixin, base.FilterView):

    raise_exception = True

    def process_name(self, object, val):
        url = reverse("management:companies_view", kwargs={"pk": object.pk})
        return '<a href="%s">%s</a>' % (url, val)

    def process_date_registered(self, object, val):
        return val.strftime(settings.DATE_FORMAT)

    def get_queryset(self, opt):

        queryset = self.get_companies()

        if "order_by" in opt and opt["order_by"]:
            queryset = queryset.order_by(opt["order_by"])

        if "search" in opt and opt["search"]:
            search_filters = (
                Q(name__icontains=opt["search"])
                | Q(account__uid__icontains=opt["search"])
                | Q(addr_postalcode__icontains=opt["search"])
                | Q(vat_number__icontains=opt["search"])
                | Q(eori__icontains=opt["search"])
            )
            queryset = queryset.filter(search_filters)

        filters = opt.get("filters", {})
        if "country" in filters:
            queryset = queryset.filter(country__name=filters["country"])
        if "obligation" in filters:
            queryset = queryset.filter(obligation__name=filters["obligation"])
        if "account" in filters:
            if filters["account"] == forms.CompanyFilters.WITHOUT_ACCOUNT:
                queryset = queryset.exclude(account__isnull=False)
            else:
                queryset = queryset.exclude(account__isnull=True)
        if "date_registered" in filters:
            start_date = self._get_startdate(filters["date_registered"])
            queryset = queryset.exclude(date_registered__lt=start_date)

        if opt["count"]:
            return queryset.count()

        return queryset[opt["offset"] : opt["limit"]]

    def _get_startdate(self, selected_option):
        today = date.today()
        if selected_option == forms.CompanyFilters.TODAY:
            start_date = today
        elif selected_option == forms.CompanyFilters.LAST_7_DAYS:
            start_date = today - timedelta(days=7)
        elif selected_option == forms.CompanyFilters.THIS_MONTH:
            start_date = date(today.year, today.month, 1)
        else:
            start_date = date(today.year, 1, 1)
        return start_date


class CompanyFilteredByAccountUID(ApiAccessMixin, CompanyMixin, generic.View):
    raise_exception = True

    def get(self, request, account_uid=None):
        data = {}
        company = self.get_account_company(uid=account_uid)
        if company:
            people = []
            for person in company.people.all():
                people.append(
                    {
                        "title": person.title,
                        "first_name": person.first_name,
                        "last_name": person.family_name,
                        "email": person.email,
                        "phone": person.phone,
                        "phone2": person.phone2,
                        "phone3": person.phone3,
                    }
                )
            data = {
                "userid": None if company.account is None else company.account.uid,
                "name": company.name,
                "date_registered": company.date_registered.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "active": company.active,
                "addr_street": company.addr_street,
                "addr_place1": company.addr_place1,
                "addr_place2": company.addr_place2,
                "country": company.country.code,
                "vat_number": company.vat_number,
                "obligation": company.obligation.code,
                "persons": people,
            }
        data = json.dumps(data, indent=4)

        return HttpResponse(data, content_type="application/json")


class CompaniesBaseView(base.ModelTableViewMixin, generic.DetailView):

    template_name = "bdr_management/company_view.html"
    model = Company
    exclude = ("id",)

    def get_context_data(self, **kwargs):
        reporting_year = SiteConfiguration.objects.get().reporting_year

        if not self.has_edit_permission():
            self.exclude = ["active", "outdated"]

        data = super(CompaniesBaseView, self).get_context_data()
        company = self.object
        statuses = company.reporting_statuses.filter(
            reporting_year__year__gte=settings.FIRST_REPORTING_YEAR
        ).filter(reporting_year__year__lte=reporting_year)
        years = [str(stat.reporting_year) for stat in statuses if stat.reported]
        data["reporting_years"] = years

        if self.object.account:
            data["has_account"] = True
        else:
            data["has_account"] = False

        if data["has_account"]:
            folder_path = self.object.build_reporting_folder_path()
            data["has_reporting_folder"] = self.object.has_reporting_folder(folder_path)
            data["reporting_folder"] = folder_path
        else:
            data["has_reporting_folder"] = False
            data["reporting_folder"] = ""

        return data

    def has_edit_permission(self):
        user = self.request.user
        group = settings.BDR_HELPDESK_GROUP

        if user.is_superuser or (
            user.is_staff and group in user.groups.values_list("name", flat=True)
        ):
            return True


class CompaniesManagementView(views.StaffuserRequiredMixin, CompaniesBaseView):

    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb("", self.object),
        ]
        data = super(CompaniesManagementView, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs

        data["person_add_url"] = reverse("management:persons_add", kwargs=self.kwargs)
        data["comment_add_url"] = reverse("management:comment_add", kwargs=self.kwargs)
        data["comment_delete_route"] = "management:comment_delete"
        data["person_route"] = "management:person_from_company"
        data["management"] = True
        data["can_view_comments"] = self.can_view_comments()
        return data

    def get_edit_url(self):
        return reverse("management:companies_edit", kwargs=self.kwargs)

    def get_delete_url(self):
        return reverse("management:companies_delete", kwargs=self.kwargs)

    def get_back_url(self):
        return reverse("management:companies")

    def can_view_comments(self):
        user = self.request.user
        group = settings.BDR_HELPDESK_GROUP

        if user.is_superuser or (
            user.is_staff and group in user.groups.values_list("name", flat=True)
        ):
            return True


class CompaniesUpdateView(base.CompanyUserRequiredMixin, CompaniesBaseView):

    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", self.object),
        ]
        data = super(CompaniesUpdateView, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs

        data["person_add_url"] = reverse("person_add", kwargs=self.kwargs)
        data["comment_add_url"] = reverse("comment_add", kwargs=self.kwargs)
        data["comment_delete_route"] = "comment_delete"
        data["person_route"] = "person"
        data["management"] = False

        return data

    def get_edit_url(self):
        return reverse("company_update", kwargs=self.kwargs)

    def get_back_url(self):
        return reverse("home")


class CompanyBaseEdit(
    base.ModelTableViewMixin, SuccessMessageMixin, CompanyMixin, generic.UpdateView
):

    template_name = "bdr_management/company_edit.html"
    model = Company
    success_message = _("Company edited successfully")
    form_class = CompanyForm


class CompaniesManagementEdit(views.GroupRequiredMixin, CompanyBaseEdit):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True

    def set_reporting_years(self, data):
        curr_year = SiteConfiguration.objects.get().reporting_year
        years = ReportingYear.objects.filter(
            year__gte=settings.FIRST_REPORTING_YEAR
        ).filter(year__lte=curr_year)
        years_dict = {}
        company = self.object
        for year in years:
            status, _ = ReportingStatus.objects.get_or_create(
                company=company, reporting_year=year
            )
            years_dict[str(year.year)] = status.reported
        data["years"] = years_dict

    def get_back_url(self):
        return reverse("management:companies_view", kwargs={"pk": self.object.pk})

    def set_breadcrumbs(self, data):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(self.get_back_url(), self.object),
            Breadcrumb("", _(u"Edit %s" % self.object)),
        ]
        data["breadcrumbs"] = breadcrumbs

    def get_context_data(self, **kwargs):
        data = super(CompaniesManagementEdit, self).get_context_data(**kwargs)
        data["management"] = True
        data["cancel_url"] = self.get_back_url()
        self.set_breadcrumbs(data)
        self.set_reporting_years(data)
        return data

    def get_form_kwargs(self):
        kwargs = super(CompaniesManagementEdit, self).get_form_kwargs()
        kwargs["obligations"] = self.get_obligations()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse("management:companies_view", kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        curr_year = SiteConfiguration.objects.get().reporting_year
        reporting_years = ReportingYear.objects.filter(
            year__gte=settings.FIRST_REPORTING_YEAR
        ).filter(year__lte=curr_year)
        company = None
        for year in reporting_years:
            submitted_val = request.POST.get(str(year.year))
            if submitted_val == "inactive":
                reported = False
            elif submitted_val == "active":
                reported = True
            else:
                reported = None
            company = Company.objects.get(pk=kwargs["pk"])
            reporting_status, created = ReportingStatus.objects.get_or_create(
                company=company, reporting_year=year, defaults={"reported": reported}
            )

            if not created:
                reporting_status.reported = reported
                reporting_status.save()

        company_name = request.POST.get("name")
        if company and company_name and company.name.strip() != company_name:
            url = settings.BDR_API_URL + "/update_organisation_name"
            form = {
                "country_code": company.country.code,
                "obligation_folder_name": company.obligation.reportek_slug,
                "account_uid": company.account.uid,
                "organisation_name": request.POST.get("name"),
            }
            requests.post(
                url, data=form, auth=settings.BDR_API_AUTH, verify=False
            )

        return super(CompanyBaseEdit, self).post(request, *args, **kwargs)


class CompaniesUpdate(base.CompanyUserRequiredMixin, CompanyBaseEdit):

    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse("company", kwargs={"pk": self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse("home"), _("Registry")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _(u"Edit %s" % self.object)),
        ]
        data = super(CompaniesUpdate, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = back_url
        data["update_view"] = True
        return data

    def get_success_url(self):
        return reverse("company", kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(CompaniesUpdate, self).get_form_kwargs()
        kwargs["obligations"] = self.get_obligations()
        kwargs["request"] = self.request
        return kwargs


class CompanyDelete(
    views.GroupRequiredMixin, base.ModelTableEditMixin, generic.DeleteView
):

    group_required = settings.BDR_HELPDESK_GROUP
    model = Company
    success_url = reverse_lazy("management:companies")
    template_name = "bdr_management/company_confirm_delete.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        back_url = reverse("management:companies_view", kwargs={"pk": self.object.pk})
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(back_url, self.object),
            Breadcrumb("", _("Delete company")),
        ]
        context = super(CompanyDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = breadcrumbs
        context["form"] = CompanyDeleteForm()
        context["cancel_url"] = back_url
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Company deleted"))
        return super(CompanyDelete, self).delete(request, *args, **kwargs)


class CompanyDeleteMultiple(views.GroupRequiredMixin, generic.TemplateView):

    group_required = settings.BDR_HELPDESK_GROUP
    success_url = reverse_lazy("management:companies")
    template_name = "bdr_management/company_confirm_delete_multiple.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb("", _("Delete multiple companies")),
        ]
        context = super(CompanyDeleteMultiple, self).get_context_data(**kwargs)
        context["breadcrumbs"] = breadcrumbs
        context["form"] = CompanyDeleteForm()
        context["cancel_url"] = self.success_url
        context["companies"] = self.get_companies()
        context["people"] = self.get_people()
        return context

    def get_company_ids(self):
        return self.request.POST.get("companies", "").split(",")

    def get_companies(self):
        return Company.objects.filter(pk__in=self.get_company_ids())

    def get_people(self):
        return Person.objects.filter(company__pk__in=self.get_company_ids())

    def delete(self, request, companies):
        messages.success(request, _("Companies deleted"))
        companies.delete()
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get("action", "")
        companies = self.get_companies()
        if not companies.exists():
            raise Http404
        if action == "delete":
            return self.delete(request, companies)
        return self.get(request, *args, **kwargs)


class CompanyAdd(
    views.GroupRequiredMixin, SuccessMessageMixin, CompanyMixin, generic.CreateView
):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/company_add.html"
    model = Company
    form_class = CompanyForm
    success_message = _("Company created successfully")

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        person_form = PersonFormWithoutCompany(self.request.POST)
        if form.is_valid() and person_form.is_valid():
            return self.form_valid(form, person_form)
        else:
            return self.form_invalid(form, person_form)

    def form_invalid(self, form, person_form):
        resp = self.get_context_data(
            form=self.get_form(self.get_form_class()), person_form=person_form
        )
        return self.render_to_response(resp)

    def form_valid(self, form, person_form):
        self.object = form.save()
        person_form.initial["company"] = self.object
        person_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("management:companies")

    def get_form_kwargs(self):
        kwargs = super(CompanyAdd, self).get_form_kwargs()
        kwargs["obligations"] = self.get_obligations()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        back_url = reverse("management:companies")
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(back_url, _("Companies")),
            Breadcrumb("", _("Add company")),
        ]
        context = super(CompanyAdd, self).get_context_data(**kwargs)
        context["breadcrumbs"] = breadcrumbs
        context["title"] = "Add a new company"
        context["cancel_url"] = back_url
        context["person_form"] = PersonFormWithoutCompany()
        return context


class ResetPassword(views.GroupRequiredMixin, SetPasswordMixin, generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/reset_password.html"
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not self.company.account:
            raise Http404
        return super(ResetPassword, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        self.company.account.set_random_password()
        backend.sync_accounts_with_ldap([self.company.account])
        msg = _("Password has been reset.")
        messages.success(request, msg)

        if request.POST.get("perform_send"):
            token = self.send_password(self.company.account)
            url = self.compose_url(
                reverse("person_set_new_password", kwargs={"token": token})
            )
            n = backend.send_password_email_to_people(self.company, url)
            messages.success(request, "Emails have been sent to %d person(s)." % n)
        return redirect("management:companies_view", pk=self.company.pk)


class ResetPasswordCompanyAccount(SetPasswordMixin, generic.DetailView):

    raise_exception = True
    template_name = "bdr_management/reset_password_company.html"
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not self.company.account:
            raise Http404
        can_edit = CanEdit(self.company)
        if not can_edit(request.user):
            return HttpResponseForbidden()
        return super(ResetPasswordCompanyAccount, self).dispatch(
            request, *args, **kwargs
        )

    def post(self, request, pk):
        self.company.account.set_random_password()
        backend.sync_accounts_with_ldap([self.company.account])
        msg = _("Password has been reset.")
        messages.success(request, msg)
        person = self.company.main_reporter
        token = self.send_password(self.company.account)
        url = self.compose_url(
            reverse("person_set_new_password", kwargs={"token": token})
        )
        backend.send_password_email_to_people(
            self.company,
            url,
            person,
            True,
            use_reset_url=True,
            send_bcc=True,
            password_reset=True,
            subject_extra=": BDR password re-set",
        )
        messages.success(request, "Email has been sent to {} .".format(person))
        if is_staff_user(request.user, self.company):
            return redirect("management:companies_view", pk=self.company.pk)
        return redirect("company", pk=self.company.pk)


class SetCompanyAccountOwner(generic.DetailView, SetPasswordMixin):

    raise_exception = True
    template_name = "bdr_management/company_account_owner.html"
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not self.company.account:
            raise Http404
        can_edit = CanEdit(self.company)
        if not can_edit(request.user):
            return HttpResponseForbidden()
        return super(SetCompanyAccountOwner, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        reporter = request.POST.get("reporter", None)
        if not reporter:
            messages.warning(request, "Person not found")
            return redirect("company", pk=self.company.pk)
        for person in self.company.people.filter(is_main_user=True):
            person.is_main_user = False
            person.save()
        person = Person.objects.get(id=reporter)
        person.is_main_user = True
        person.save()
        token = self.send_password(self.company.account)
        url = self.compose_url(
            reverse("person_set_new_password", kwargs={"token": token})
        )
        backend.send_password_email_to_people(
            self.company,
            url,
            person,
            self.company.account,
            use_reset_url=True,
            send_bcc=True,
            subject_extra=": New owner BDR password re-set",
            set_owner=True,
        )
        messages.success(
            request,
            "Person {} has been set as company account owner.A password reset e-mail has been sent to this person.".format(
                person
            ),
        )
        if is_staff_user(request.user, self.company):
            return redirect("management:companies_view", pk=self.company.pk)
        return redirect("company", pk=self.company.pk)


class CreateAccountPerson(generic.DetailView, SetPasswordMixin):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/create_account_for_person.html"
    model = Person

    def dispatch(self, request, *args, **kwargs):
        self.person = self.get_object()
        if self.person.account:
            raise Http404
        company = self.person.company
        can_edit = CanEdit(company)
        if not can_edit(request.user):
            return HttpResponseForbidden()
        return super(CreateAccountPerson, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        account = Account.objects.create_for_person(self.person.company, self.person)
        account.set_random_password()
        self.person.account = account
        self.person.save()
        backend.sync_accounts_with_ldap([account], True)
        set_role_for_person_account(request, self.person.company, self.person, "add")
        msg = "Account created."
        messages.success(request, msg)
        if request.POST.get("perform_send"):
            token = self.send_password(account)
            url = self.compose_url(
                reverse("person_set_new_password", kwargs={"token": token})
            )
            n = backend.send_password_email_to_people(
                self.person.company,
                url,
                self.person,
                use_reset_url=True,
                send_bcc=True,
                personal_account=True,
            )
            messages.success(request, "Emails have been sent to %d person(s)." % n)
        return redirect("person", pk=self.person.pk)


class DisableAccountPerson(generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/disable_account_for_person.html"
    model = Person

    def dispatch(self, request, *args, **kwargs):
        self.person = self.get_object()
        if not self.person.account:
            raise Http404
        company = self.person.company
        can_edit = CanEdit(company)
        if not can_edit(request.user):
            return HttpResponseForbidden()
        return super(DisableAccountPerson, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        account = self.person.account
        user = User.objects.get(username=account.uid)
        user.is_active = False
        user.save()
        set_role_for_person_account(request, self.person.company, self.person, "remove")
        return redirect("person", pk=self.person.pk)


class EnableAccountPerson(generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/enable_account_for_person.html"
    model = Person

    def dispatch(self, request, *args, **kwargs):
        self.person = self.get_object()
        if not self.person.account:
            raise Http404
        company = self.person.company
        can_edit = CanEdit(company)
        if not can_edit(request.user):
            return HttpResponseForbidden()
        return super(EnableAccountPerson, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        account = self.person.account
        user = User.objects.get(username=account.uid)
        user.is_active = True
        user.save()
        set_role_for_person_account(request, self.person.company, self.person, "add")
        return redirect("person", pk=self.person.pk)


class CreateAccount(views.GroupRequiredMixin, SetPasswordMixin, generic.DetailView):

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/create_account.html"
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if self.company.account:
            raise Http404
        return super(CreateAccount, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        obligation = self.company.obligation
        account = Account.objects.create_for_obligation(obligation)
        account.set_random_password()
        self.company.account = account
        self.company.save()
        backend.sync_accounts_with_ldap([account])
        msg = "Account created."
        messages.success(request, msg)

        if request.POST.get("perform_send"):
            token = self.send_password(account)
            url = self.compose_url(
                reverse("person_set_new_password", kwargs={"token": token})
            )
            n = backend.send_password_email_to_people(self.company, url)
            messages.success(request, "Emails have been sent to %d person(s)." % n)
        return redirect("management:companies_view", pk=self.company.pk)


class CreateReportingFolder(views.GroupRequiredMixin, generic.DetailView):

    API_ERROR_MSG = "BDR_API_URL and BDR_API_AUTH not configured"

    group_required = settings.BDR_HELPDESK_GROUP
    raise_exception = True
    template_name = "bdr_management/create_reporting_folder.html"
    model = Company

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_object()
        if not (settings.BDR_API_URL and settings.BDR_API_AUTH):
            messages.error(request, self.API_ERROR_MSG)
            return redirect("management:companies_view", pk=self.company.pk)
        return super(CreateReportingFolder, self).dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        url = settings.BDR_API_URL + "/create_organisation_folder"
        form = {
            "country_code": self.company.country.code,
            "obligation_folder_name": self.company.obligation.reportek_slug,
            "account_uid": self.company.account.uid,
            "organisation_name": self.company.name,
        }
        resp = requests.post(url, data=form, auth=settings.BDR_API_AUTH, verify=False)

        if resp.status_code != 200:
            messages.error(request, "BDR API request failed: %s" % resp)
        elif "unauthorized" in bytes.decode(resp.content.lower()):
            messages.error(request, "BDR API request failed: Unauthorized")
        else:
            rv = resp.json()
            success = rv["success"]
            if success:
                if rv["created"]:
                    messages.success(request, "Created: %s" % rv["path"])
                else:
                    messages.warning(request, "Existing: %s" % rv["path"])
            else:
                messages.error(request, "Error: %s" % rv["error"])

        return redirect("management:companies_view", pk=self.company.pk)


class CompanyNameHistory(views.StaffuserRequiredMixin, generic.DetailView):

    template_name = "bdr_management/company_name_history.html"
    model = Company
    raise_exception = True

    def get_context_data(self, **kwargs):
        company = kwargs["object"]
        back_url = reverse("management:companies_view", kwargs={"pk": company.pk})
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb(reverse("management:companies"), _("Companies")),
            Breadcrumb(back_url, kwargs["object"]),
            Breadcrumb("", _("Name history")),
        ]
        context = super(CompanyNameHistory, self).get_context_data()
        context["breadcrumbs"] = breadcrumbs

        return context
