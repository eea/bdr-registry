import json
import xmltodict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from bdr_management.base import ApiAccessMixin
from bdr_registry.models import Company, Obligation


class CompanyAllView(ApiAccessMixin, View):
    def get(self, request, *args, **kwargs):

        data = []
        account_uid = request.GET.get("account_uid")
        for company in Company.objects.all():
            if account_uid is not None:
                if company.account is None or company.account.uid != account_uid:
                    continue
            item = OrderedDict(
                (k, getattr(company, k))
                for k in [
                    "pk",
                    "name",
                    "addr_street",
                    "addr_postalcode",
                    "eori",
                    "vat_number",
                    "addr_place1",
                    "addr_place2",
                    "active",
                ]
            )
            if company.account is not None:
                item["account"] = company.account.uid
            if company.obligation is not None:
                item["obligation"] = {
                    "@name": company.obligation.name,
                    "#text": company.obligation.code,
                }
            item["country"] = {
                "@name": getattr(company.country, "name", ""),
                "#text": getattr(company.country, "code", ""),
            }

            def person_data(person):
                phones = [person.phone, person.phone2, person.phone3]
                return OrderedDict(
                    [
                        ("name", "{p.first_name} {p.family_name}".format(p=person)),
                        ("email", person.email),
                        ("phone", [p for p in phones if p]),
                        ("fax", person.fax),
                    ]
                )

            item["person"] = [person_data(p) for p in company.people.all()]

            def comment_data(comment):
                return OrderedDict(
                    [("text", comment.text), ("created", comment.created)]
                )

            item["comment"] = [comment_data(c) for c in company.comments.all()]

            data.append(item)
        xml = xmltodict.unparse({"organisations": {"organisation": data}})
        return HttpResponse(xml, content_type="application/xml")


class CompanyByObligationView(ApiAccessMixin, View):
    def get(self, request, *args, **kwargs):
        obligation_slug = kwargs["obligation_slug"]
        obligation = get_object_or_404(Obligation, reportek_slug=obligation_slug)
        DATE_FORMAT = "%Y/%m/%d %H:%I:%s"
        fields = [
            "pk",
            "name",
            "addr_street",
            "addr_postalcode",
            "eori",
            "vat_number",
            "addr_place1",
            "addr_place2",
            "active",
            "website",
        ]
        data = []

        for company in obligation.companies.all():
            d = {field: getattr(company, field) for field in fields}
            d["country"] = dict(
                code=getattr(company.country, "code", ""),
                name=getattr(company.country, "name", ""),
            )
            d["date_registered"] = company.date_registered.strftime(DATE_FORMAT)
            d["account"] = company.account and company.account.uid
            data.append(d)
        return HttpResponse(json.dumps(data), content_type="application/json")
