import re
from django import template


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
