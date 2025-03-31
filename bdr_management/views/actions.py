from braces import views
import csv
import json
from datetime import datetime
import xlsxwriter
from io import BytesIO

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext as _
from django.views import generic


from bdr_management import backend
from bdr_management.base import Breadcrumb, ApiAccessMixin

from bdr_registry.models import (
    Account,
    Obligation,
    Company,
    Person,
    ReportingStatus,
    ReportingYear,
    SiteConfiguration,
)
from bdr_management.views.mixins import CompanyMixin


class Actions(views.StaffuserRequiredMixin, generic.TemplateView):

    template_name = "bdr_management/actions.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        config = SiteConfiguration.objects.get()
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Actions")),
        ]
        data = super(Actions, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        curr_year = config.reporting_year
        last_year = curr_year - 1
        data['obligations'] = self.request.user.obligations.all()
        data["curr_year"] = curr_year
        data["last_year"] = last_year
        return data


class CopyReportingStatus(views.StaffuserRequiredMixin, CompanyMixin, generic.View):

    raise_exception = True

    def get(self, request):
        copied = 0

        curr_year_int = SiteConfiguration.objects.get().reporting_year
        prev_year_int = curr_year_int - 1

        try:
            prev_year_obj = ReportingYear.objects.get(year=prev_year_int)
            curr_year_obj = ReportingYear.objects.get(year=curr_year_int)
        except ObjectDoesNotExist:
            messages.error(request, _("Previous or current year data not found"))
            return HttpResponseRedirect(reverse("management:actions"))

        companies = self.get_companies()

        for company in companies:

            reporting_stat, created = company.reporting_statuses.get_or_create(
                company=company, reporting_year=curr_year_obj
            )
            if reporting_stat.reported is None:
                prev_reporting_stat, created = ReportingStatus.objects.get_or_create(
                    company=company, reporting_year=prev_year_obj
                )
                if prev_reporting_stat.reported is not None:
                    reporting_stat.reported = prev_reporting_stat.reported
                    reporting_stat.save()
                    copied += 1
        messages.success(request, _("Data copied for %s companies." % copied))

        return HttpResponseRedirect(reverse("management:actions"))


class CompaniesJsonExport(ApiAccessMixin, CompanyMixin, generic.View):

    raise_exception = True

    def get(self, request):

        companies = []

        user_obligations = self.get_obligations(no_user=self.no_user)
        selected_obligation = Obligation.objects.filter(code=self.request.GET.get('obligation', '')).first()
        if selected_obligation:
            user_obligations = [selected_obligation.id]
        companies_list = Company.objects.filter(obligation__id__in=user_obligations).all()

        for company in companies_list:
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

            companies.append(
                {
                    "userid": None if company.account is None else company.account.uid,
                    "name": company.name,
                    "date_registered": company.date_registered.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "active": company.active,
                    "outdated": company.outdated,
                    "addr_street": company.addr_street,
                    "addr_place1": company.addr_place1,
                    "addr_place2": company.addr_place2,
                    "country": "" if not company.country else company.country.code,
                    "country_name": "" if not company.country else company.country.name,
                    "vat_number": company.vat_number,
                    "world_manufacturer_identifier": company.world_manufacturer_identifier,
                    "obligation": company.obligation.code,
                    "persons": people,
                }
            )

        data = json.dumps(companies, indent=4)

        return HttpResponse(data, content_type="application/json")


class CompaniesExcelExport(ApiAccessMixin, CompanyMixin, generic.View):

    raise_exception = True

    def generate_excel_file(self, workbook):
        header = [
            "userid",
            "name",
            "date_registered",
            "active",
            "outdated",
            "addr_street",
            "addr_place1",
            "addr_postalcode",
            "addr_place2",
            "country",
            "vat_number",
            "world_manufacturer_identifier",
            "obligation",
            "person_title",
            "person_first_name",
            "person_family_name",
            "person_email",
            "person_phone",
            "person_phone2",
            "person_phone3",
        ]

        format_cols_headers = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 12,
                "text_wrap": True,
                "border": 1,
            }
        )
        format_rows = workbook.add_format(
            {
                "align": "left",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 12,
                "text_wrap": True,
            }
        )

        worksheet = workbook.add_worksheet("Companies")
        worksheet.set_column("A1:Q1", 30)
        worksheet.set_column("Q1:Q1", 50)
        worksheet.set_column("R1:T1", 20)
        worksheet.write_row("A1", header, format_cols_headers)
        user_obligations = self.get_obligations(no_user=self.no_user)
        selected_obligation = Obligation.objects.filter(code=self.request.GET.get('obligation', '')).first()
        if selected_obligation:
            user_obligations = [selected_obligation.id]
        companies = Company.objects.filter(obligation__id__in=user_obligations).all()
        index = 1

        for company in companies:
            account = company.account
            company_data = [
                "" if account is None else account.uid,
                company.name or "",
                company.date_registered.strftime("%Y-%m-%d %H:%M:%S"),
                "on" if company.active else "",
                "on" if company.outdated else "",
                company.addr_street or "",
                company.addr_place1 or "",
                company.addr_postalcode or "",
                company.addr_place2 or "",
                "" if not company.country else (company.country.name or ""),
                company.vat_number or "",
                company.world_manufacturer_identifier or "",
                company.obligation.code if company.obligation else "",
            ]
            people_count = company.people.all().count()

            if people_count >= 2:
                count = 0
                for field in company_data:
                    worksheet.merge_range(
                        index,
                        count,
                        index + people_count - 1,
                        count,
                        field,
                        format_rows,
                    )
                    count += 1
                for person in company.people.all():
                    data = [
                        person.title or "",
                        person.first_name or "",
                        person.family_name or "",
                        person.email or "",
                        person.phone or "",
                        person.phone2 or "",
                        person.phone3 or "",
                    ]
                    worksheet.write_row(index, count, data, format_rows)
                    index += 1
            elif people_count == 1:
                person = company.people.first()
                person_data = [
                    person.title or "",
                    person.first_name or "",
                    person.family_name or "",
                    person.email or "",
                    person.phone or "",
                    person.phone2 or "",
                    person.phone3 or "",
                ]
                worksheet.write_row(
                    index,
                    0,
                    company_data + person_data,
                    format_rows,
                )
                index += 1
            else:
                worksheet.write_row(
                    index, 0, company_data + ["", "", "", "", "", "", ""], format_rows
                )
                index += 1

    def get(self, request):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_excel_file(workbook)
        workbook.close()
        output.seek(0)
        date = datetime.now().strftime("%Y_%m_%d")
        filename = "_".join([date, "companies_export"]) + ".xlsx"
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class CompaniesCsvExport(ApiAccessMixin, generic.View):
    raise_exception = True

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="companies.csv"'

        companies = Company.objects.filter(obligation__name="F-gases")

        writer = csv.writer(response)
        writer.writerow(
            [
                "Company name",
                "Date registered",
                "Active",
                "Outdated",
                "Address street",
                "Postal Code",
                "Address place 1",
                "Address place 2",
                "EORI",
                "VAT",
                "Country",
                "Website",
                "Obligation",
            ]
        )
        for c in companies:
            row = [
                c.name,
                c.date_registered.isoformat(),
                c.active,
                c.outdated,
                c.addr_street,
                c.addr_postalcode,
                c.addr_place1,
                c.addr_place2,
                c.eori,
                c.vat_number,
                c.country.name,
                c.website,
                c.obligation.name,
            ]
            row = map(lambda x: x.encode("utf-8") if isinstance(x, str) else x, row)
            writer.writerow(row)

        return response


class PersonsExport(ApiAccessMixin, CompanyMixin, generic.View):

    raise_exception = True

    def get(self, request):

        header = [
            "userid",
            "companyname",
            "country",
            "contactname",
            "contactemail",
            "account",
            "phone",
            "phone2",
            "phone3",
            "fax",
        ]
        rows = []

        user_obligations = self.get_obligations(no_user=self.no_user)
        selected_obligation = Obligation.objects.filter(code=request.GET.get('obligation', '')).first()
        if selected_obligation:
            user_obligations = [selected_obligation.id]

        persons = Person.objects.filter(
            company__obligation__id__in=user_obligations
        ).all()
        for person in persons:
            org = person.company
            account = org.account
            if account is None:
                continue
            rows.append(
                [
                    v.encode("utf-8") if v else ""
                    for v in [
                        account.uid,
                        org.name,
                        org.country.name,
                        f"{person.title or '' } {person.first_name} {person.family_name}",
                        person.email,
                        getattr(person.account, "uid", ""),
                        person.phone,
                        person.phone2,
                        person.phone3,
                        person.fax,
                    ]
                ]
            )
        xls_doc = backend.generate_excel(header, rows)
        return HttpResponse(xls_doc, content_type="application/vnd.ms-excel")


class PersonsExportJson(ApiAccessMixin, CompanyMixin, generic.View):

    raise_exception = True

    def get(self, request):

        persons = []

        user_obligations = self.get_obligations(no_user=self.no_user)

        persons_list = Person.objects.filter(
            company__obligation__id__in=user_obligations
        ).all()

        for person in persons_list:
            org = person.company
            account = org.account
            if account is None:
                continue
            persons.append(
                {
                    "userid": account.uid,
                    "companyname": org.name,
                    "country": org.country.name,
                    "contactname": (
                        "{p.title} {p.first_name} {p.family_name}".format(p=person)
                    ),
                    "contactemail": person.email,
                    "phone": person.phone,
                    "phone2": person.phone2,
                    "phone3": person.phone3,
                    "fax": person.fax,
                }
            )

        data = json.dumps(persons, indent=4)

        return HttpResponse(data, content_type="application/json")


class CompaniesForUsernameView(ApiAccessMixin, generic.View):
    def get(self, request):
        username = request.GET.get("username", "")
        data = []
        account = Account.objects.filter(uid=username)
        if account:
            account = account.first()
            companies = []
            if hasattr(account, "persons"):
                if account.persons.all().count() != 0:
                    companies = [person.company for person in account.persons.all()]
            if hasattr(account, "companies"):
                if account.companies.all().count() != 0:
                    companies = account.companies.all()
            for company in companies:
                folder_path = company.build_reporting_folder_path()
                has_reporting_folder = company.has_reporting_folder(folder_path)
                if has_reporting_folder:
                    reporting_folder = company.build_reporting_folder_path()
                else:
                    reporting_folder = ""

                registry_url = reverse("company", kwargs={"pk": company.id}).strip("/")
                company_data = {
                    "company_name": company.name,
                    "reporting_folder": reporting_folder,
                    "has_reporting_folder": has_reporting_folder,
                    "registry_url": "/".join(["/registry", registry_url]),
                }
                data.append(company_data)
        return HttpResponse(json.dumps(data), content_type="application/json")
