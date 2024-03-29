from datetime import datetime
import re
import requests
from requests.auth import HTTPBasicAuth

from django import template
from django.conf import settings
from django.urls import reverse
from django.template.defaultfilters import urlize
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

import bdr_management
from bdr_registry.models import Company, EmailTemplate, Person, Account
from bdr_registry.settings import (
    BDR_SIDEMENU_URL,
    BDR_API_AUTH_USER,
    BDR_API_AUTH_PASSWORD,
)

register = template.Library()
numeric_test = re.compile("^\d+$")


@register.simple_tag
def assign(value):
    return value


@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    if isinstance(value, dict) and arg in value:
        return value[arg]
    return None


@register.filter
def process_field(value, management):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime(settings.DATE_FORMAT)
    if isinstance(value, Company):
        if management:
            return mark_safe(
                '<a href="%s">%s</a'
                % (
                    reverse("management:companies_view", kwargs={"pk": value.pk}),
                    str(value),
                )
            )
        else:
            return mark_safe(
                '<a href="%s">%s</a'
                % (reverse("company", kwargs={"pk": value.pk}), str(value))
            )
    if isinstance(value, EmailTemplate):
        return mark_safe(
            '<a href="%s">%s</a'
            % (
                reverse("management:email_template_view", kwargs={"pk": value.pk}),
                str(value),
            )
        )
    return urlize(value)


@register.filter
def has_permission(user, object):

    if object and isinstance(object, Company):
        company = object
    elif object and hasattr(object, "company"):
        company = object.company
    else:
        company = None

    return bdr_management.base.has_permission(user, company)


@register.filter
def is_staff_or_company_account(user, object):
    if object and isinstance(object, Company):
        company = object
    elif object and hasattr(object, "company"):
        company = object.company
    else:
        company = None

    if user.is_superuser:
        return True

    account = company.account
    if account is not None:
        if account.uid == user.username:
            return True

    return False


@register.filter
def is_company_account(user, object):
    if object and isinstance(object, Company):
        company = object
    elif object and hasattr(object, "company"):
        company = object.company
    else:
        company = None

    account = company.account
    if account is not None:
        if account.uid == user.username:
            return True

    return False


@register.filter
def is_persons_account(user, object):
    if object and isinstance(object, Person):
        person = object

    account = person.account
    if account is not None:
        if account.uid == user.username:
            return True

    return False


@register.filter
def is_a_personal_account(user):
    account = Account.objects.filter(uid=user.username)
    if account:
        person = hasattr(account.first(), "person")
        if person:
            return True
    return False


@register.filter
def custom_render_field(field):
    attrs = {}
    if field.errors:
        attrs = {"class": "form-error"}
    context = {
        "label": field.label_tag(),
        "input": field.as_widget(attrs=attrs),
        "errors": [err for err in field.errors],
    }
    return render_to_string("bits/custom_field.html", context)


@register.simple_tag
def get_sidebar(user):
    params = {"username": user.username}
    response = requests.get(
        BDR_SIDEMENU_URL,
        params=params,
        auth=HTTPBasicAuth(BDR_API_AUTH_USER, BDR_API_AUTH_PASSWORD),
    )
    if response.status_code == 200:
        return mark_safe(response.text)
