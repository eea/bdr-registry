import xmltodict
import json
from functools import wraps
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.core import serializers

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from bdr_registry import models


def api_key_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        apikey = request.GET.get('apikey', '')
        if models.ApiKey.objects.filter(key=apikey).count() < 1:
            return HttpResponseForbidden(
                "Invalid API key, please set correct 'apikey' GET parameter.")
        return view(request, *args, **kwargs)

    return wrapper


@api_key_required
def company_all(request):
    data = []
    account_uid = request.GET.get('account_uid')
    for company in models.Company.objects.all():
        if account_uid is not None:
            if (company.account is None or
                        company.account.uid != account_uid):
                continue
        item = OrderedDict((k, getattr(company, k))
                           for k in
                           ['pk', 'name', 'addr_street', 'addr_postalcode',
                            'eori', 'vat_number', 'addr_place1',
                            'addr_place2'])
        if company.account is not None:
            item['account'] = company.account.uid
        if company.obligation is not None:
            item['obligation'] = {
                '@name': company.obligation.name,
                '#text': company.obligation.code,
            }
        item['country'] = {
            '@name': company.country.name,
            '#text': company.country.code,
        }

        def person_data(person):
            phones = [person.phone, person.phone2, person.phone3]
            return OrderedDict([
                ('name', u"{p.first_name} {p.family_name}".format(p=person)),
                ('email', person.email),
                ('phone', [p for p in phones if p]),
                ('fax', person.fax),
            ])

        item['person'] = [person_data(p) for p in company.people.all()]

        def comment_data(comment):
            return OrderedDict([
                ('text', comment.text),
                ('created', comment.created)
            ])

        item['comment'] = [comment_data(c) for c in company.comments.all()]

        data.append(item)
    xml = xmltodict.unparse({'organisations': {'organisation': data}})
    return HttpResponse(xml, content_type='application/xml')


@api_key_required
def company_by_obligation(request, obligation_slug):
    obligation = get_object_or_404(models.Obligation,
                                   reportek_slug=obligation_slug)
    fields = [
        'pk', 'name', 'addr_street', 'addr_postalcode', 'eori', 'vat_number',
        'addr_place1', 'addr_place2', 'active', 'website', 'date_registered',
    ]
    data = []
    for company in obligation.companies.all():
        d = {field: getattr(company, field) for field in fields}
        d['country'] = dict(code=company.country.code,
                            name=company.country.name)
        data.append(d)
    return HttpResponse(json.dumps(data), content_type='application/json')
