from braces.views import AjaxResponseMixin, JSONResponseMixin
from braces.views._access import AccessMixin
from collections import namedtuple

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.views.generic import View

from bdr_registry.models import Account, ApiKey, Company, Person


Breadcrumb = namedtuple("Breadcrumb", ["url", "title"])


class CompanyUserRequiredBaseMixin(AccessMixin):

    group_required = settings.BDR_HELPDESK_GROUP

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.company = self.get_company()

        if not has_permission(self.request.user, self.company):
            if self.raise_exception:
                raise PermissionDenied
            else:
                return redirect_to_login(
                    request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name(),
                )

        return super(CompanyUserRequiredBaseMixin, self).dispatch(
            request, *args, **kwargs
        )


class CompanyUserRequiredMixin(CompanyUserRequiredBaseMixin):
    def get_company(self):
        return get_object_or_404(Company, pk=self.kwargs["pk"])


class PersonUserRequiredMixin(CompanyUserRequiredBaseMixin):
    def get_company(self):
        person = get_object_or_404(Person, pk=self.kwargs["pk"])
        return person.company


class FilterView(JSONResponseMixin, AjaxResponseMixin, View):
    def get_queryset(self, options):
        raise NotImplementedError

    def _process_field_value(self, value):
        if isinstance(value, Model):
            return str(value)
        return value

    def get_ajax(self, request):
        args = request.GET

        columns = args["sColumns"].split(",")
        limit = int(args.get("iDisplayLength", 10)) + int(args.get("iDisplayStart", 0))
        get_rows = {
            "offset": int(args.get("iDisplayStart", 0)),
            "limit": limit,
            "count": False,
        }

        get_limit = {
            "offset": 0,
            "limit": None,
            "count": True,
        }

        with_filter = {
            "search": args.get("sSearch", ""),
            "order_by": (),
        }

        no_filter = {
            "search": "",
        }

        # Python 2.6 doesn't have dict comprehension, so instead of
        # filters = {columns[i]: args.get('sSearch_%s' % i)
        #            for i in range(len(columns)) if args.get('sSearch_%s' % i)}
        # do:
        filters = dict(
            (columns[i], args.get("sSearch_%s" % i))
            for i in range(len(columns))
            if args.get("sSearch_%s" % i)
        )

        with_filter["filters"] = filters

        nr_of_sorting_cols = int(args.get("iSortingCols", 0))
        if nr_of_sorting_cols > 0:
            column = columns[int(args.get("iSortCol_0", 0))]
            direction = args.get("sSortDir_0", "asc")
            with_filter["order_by"] = column
            if direction == "desc":
                with_filter["order_by"] = "-%s" % column

        options = dict(with_filter, **get_rows)
        table_data = []
        for row in self.get_queryset(options):
            row_data = []
            for column in columns:
                callback = getattr(self, "process_%s" % column, None)
                column_value = self._process_field_value(getattr(row, column, None))
                if callback:
                    row_data.append(callback(row, column_value))
                else:
                    row_data.append(column_value)
            table_data.append(row_data)

        count_filtered = self.get_queryset(dict(with_filter, **get_limit))
        count_total = self.get_queryset(dict(no_filter, **get_limit))

        return self.render_json_response(
            {
                "iTotalRecords": count_total,
                "iTotalDisplayRecords": count_filtered,
                "aaData": table_data,
            }
        )


class ModelTableMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ModelTableMixin, self).get_context_data(**kwargs)
        context["fields"] = self._get_model_fields()
        context["edit_url"] = self.get_edit_url()
        context["delete_url"] = self.get_delete_url()
        context["back_url"] = self.get_back_url()
        return context

    def get_edit_url(self):
        return getattr(self, "edit_url", None)

    def get_delete_url(self):
        return getattr(self, "delete_url", None)

    def get_back_url(self):
        return getattr(self, "back_url", None)

    def _get_model_fields(self):
        model = getattr(self, "model", None)
        fields = getattr(self, "fields", [])
        exclude = getattr(self, "exclude", [])

        if not model:
            raise ImproperlyConfigured("ModelTableMixin requires a definition of model")
        model_fields = model._meta.fields
        if fields:
            model_fields = filter(lambda x: x.name in fields, model_fields)
        if exclude:
            model_fields = filter(lambda x: x.name not in exclude, model_fields)
        return model_fields


class ModelTableEditMixin(ModelTableMixin):

    template_name = "bdr_management/_edit.html"


class ModelTableViewMixin(ModelTableMixin):

    template_name = "bdr_management/_view.html"


def has_permission(user, company):
    if user.is_superuser:
        return True
    required_group = settings.BDR_HELPDESK_GROUP
    if required_group in user.groups.values_list("name", flat=True):
        return True

    if company:
        account = company.account
        if account and (account.uid == user.username):
            return True
        account = Account.objects.filter(uid=user.username)
        if not account:
            return False
        account = account.first()
        for person in account.persons.all():
            if person.company == company:
                return True
    return False


def is_staff_user(user, company):
    if user.is_superuser:
        return True
    required_group = settings.BDR_HELPDESK_GROUP
    if required_group in user.groups.values_list("name", flat=True):
        return True
    return False


class ApiAccessMixin(AccessMixin):

    no_user = False

    def dispatch(self, request, *args, **kwargs):
        token = ApiKey.objects.first().key
        authorization = request.META.get("HTTP_AUTHORIZATION", "")
        # authorization is actually looking for the header Authorization, but from Django's
        # behavior this header is found in META, keyword HTTP_AUTHORIZATION
        authorization_non_header = request.GET.get("apikey", "")
        if authorization or authorization_non_header:
            self.no_user = True
        if (
            request.user.is_staff
            or authorization == token
            or authorization_non_header == token
        ):
            return super(ApiAccessMixin, self).dispatch(request, *args, **kwargs)
        return self.handle_no_permission(request)
