import re
from datetime import datetime
from django import template
from django.conf import settings
from django.template.defaultfilters import urlize


register = template.Library()
numeric_test = re.compile('^\d+$')


@register.assignment_tag
def assign(value):
    return value


@register.filter
def getattribute(value, arg):
    """ Gets an attribute of an object dynamically from a string name """

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    if isinstance(value, dict) and arg in value:
        return value[arg]
    return None


@register.filter
def process_field(value):
    if isinstance(value, datetime):
        return value.strftime(settings.DATE_FORMAT)
    return urlize(value)


@register.filter
def group_required(user, group_name):
    if user.is_superuser:
        return True

    if group_name in user.groups.values_list('name', flat=True):
        return True

    return False

