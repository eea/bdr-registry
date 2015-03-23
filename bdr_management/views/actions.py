import json
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views import generic

from braces import views
from django.contrib import messages
from bdr_management import backend

from bdr_management.base import Breadcrumb
from bdr_registry.models import (ReportingYear, Company, ReportingStatus,
                                 Person, SiteConfiguration)
from bdr_management.views.mixins import CompanyMixin


class Actions(views.StaffuserRequiredMixin,
              generic.TemplateView):

    template_name = 'bdr_management/actions.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        config = SiteConfiguration.objects.get()
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _('Actions')),
        ]
        data = super(Actions, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        curr_year = config.reporting_year
        last_year = curr_year - 1
        data['curr_year'] = curr_year
        data['last_year'] = last_year
        return data


class CopyReportingStatus(views.StaffuserRequiredMixin,
                          CompanyMixin,
                          generic.View):

    raise_exception = True

    def get(self, request):
        copied = 0

        curr_year_int = SiteConfiguration.objects.get().reporting_year
        prev_year_int = curr_year_int - 1

        try:
                prev_year_obj = ReportingYear.objects.get(year=prev_year_int)
                curr_year_obj = ReportingYear.objects.get(year=curr_year_int)
        except ObjectDoesNotExist:
            messages.error(request,
                           _('Previous or current year data not found'))
            return HttpResponseRedirect(reverse('management:actions'))

        companies = self.get_companies()

        for company in companies:

            reporting_stat, created = company.reporting_statuses.get_or_create(
                company=company,
                reporting_year=curr_year_obj
            )
            if reporting_stat.reported is None:
                prev_reporting_stat, created = ReportingStatus.objects.get_or_create(
                    company=company,
                    reporting_year=prev_year_obj
                )
                if prev_reporting_stat.reported is not None:
                    reporting_stat.reported = prev_reporting_stat.reported
                    reporting_stat.save()
                    copied += 1
        messages.success(request,
                         _('Data copied for %s companies.' % copied))

        return HttpResponseRedirect(reverse('management:actions'))


class CompaniesJsonExport(views.StaffuserRequiredMixin,
                          CompanyMixin,
                          generic.View):

    raise_exception = True

    def get(self, request):

        companies = []

        companies_list = self.get_companies()

        for company in companies_list:

            people = []
            for person in company.people.all():
                people.append({
                    'title': person.title,
                    'first_name': person.first_name,
                    'last_name': person.family_name,
                    'email': person.email,
                    'phone': person.phone,
                    'phone2': person.phone2,
                    'phone3': person.phone3
                })

            companies.append({
                'userid': None if company.account is None else company.account.uid,
                'name': company.name,
                'date_registered': company.date_registered.strftime('%Y-%m-%d %H:%M:%S'),
                'active': company.active,
                'addr_street': company.addr_street,
                'addr_place1': company.addr_place1,
                'addr_place2': company.addr_place2,
                'country': company.country.code,
                'vat_number': company.vat_number,
                'obligation': company.obligation.code,
                'persons': people
            })

        data = json.dumps(companies, indent=4)

        return HttpResponse(data, content_type="application/json")


class CompaniesExcelExport(views.StaffuserRequiredMixin,
                           CompanyMixin,
                           generic.View):

    raise_exception = True

    def get(self, request):
        header = ['userid', 'name', 'date_registered', 'active',
                  'addr_street', 'addr_place1', 'addr_postalcode',
                  'addr_place2', 'country', 'vat_number', 'obligation']
        rows = []

        companies = self.get_companies()

        for company in companies:
            account = company.account
            rows.append([v.encode('utf-8') for v in [
                '' if account is None else account.uid,
                company.name,
                company.date_registered.strftime('%Y-%m-%d %H:%M:%S'),
                'on' if company.active else '',
                company.addr_street,
                company.addr_place1,
                company.addr_postalcode,
                company.addr_place2,
                company.country.name,
                company.vat_number or '',
                company.obligation.code if company.obligation else '',
            ]])

        xls_doc = backend.generate_excel(header, rows)
        return HttpResponse(xls_doc, content_type="application/vnd.ms-excel")


class CompaniesCsvExport(views.StaffuserRequiredMixin,
                         generic.View):
    raise_exception = True

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="companies.csv"'

        companies = Company.objects.filter(active=False,
                                           obligation__name="F-gases")

        writer = csv.writer(response)
        writer.writerow(["Company name", "Date registered", "Address street",
                         "Postal Code", "Address place 1", "Address place 2",
                         "EORI", "VAT", "Country", "Website", "Obligation"])
        for c in companies:
            row = [c.name, c.date_registered.isoformat(), c.addr_street,
                   c.addr_postalcode, c.addr_place1, c.addr_place2, c.eori,
                   c.vat_number, c.country.name, c.website, c.obligation.name]
            row = map(lambda x: x.encode("utf-8") if isinstance(x, unicode) else x, row)
            writer.writerow(row)

        return response


class PersonsExport(views.StaffuserRequiredMixin,
                    CompanyMixin,
                    generic.View):

    raise_exception = True

    def get(self, request):

        header = ['userid', 'companyname', 'country',
                  'contactname', 'contactemail', 'phone', 'phone2', 'phone3',
                  'fax']
        rows = []

        user_obligations = self.get_obligations()

        persons = (
            Person.objects.filter(company__obligation__id__in=user_obligations)
            .all()
        )

        for person in persons:
            org = person.company
            account = org.account
            if account is None:
                continue
            rows.append([v.encode('utf-8') if v else '' for v in [
                account.uid,
                org.name,
                org.country.name,
                u"{p.title} {p.first_name} {p.family_name}".format(p=person),
                person.email,
                person.phone,
                person.phone2,
                person.phone3,
                person.fax,
            ]])
        xls_doc = backend.generate_excel(header, rows)
        return HttpResponse(xls_doc, content_type="application/vnd.ms-excel")
