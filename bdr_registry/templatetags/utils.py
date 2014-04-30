from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import re
from datetime import datetime

from django import template
from django.conf import settings
from django.template.defaultfilters import urlize

from xml.etree import ElementTree

import bdr_management
from bdr_registry.models import Company

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
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime(settings.DATE_FORMAT)
    if isinstance(value, Company):
        return mark_safe('<a href="%s">%s</a' % (
            reverse('company', kwargs={'pk': value.pk}),
            unicode(value)))
    return urlize(value)


@register.filter
def has_permission(user, object):

    if object and isinstance(object, Company):
        company = object
    elif object and hasattr(object, 'company'):
        company = object.company
    else:
        company = None

    return bdr_management.base.has_permission(user, company)


@register.filter
def custom_render_field(field):
    div = ElementTree.Element('div')
    div.attrib['class'] = 'form-group'
    label = ElementTree.fromstring(field.label_tag().encode('utf-8'))
    if field.field.required:
        label.attrib['class'] = 'required'
    div.append(label)
    input_elem = ElementTree.fromstring(field.as_widget().encode('utf-8'))
    if field.errors:
        input_elem.attrib['class'] = 'form-error'
    div.append(input_elem)

    for err in field.errors:
        err_div = ElementTree.Element('div')
        err_div.text = err
        err_div.attrib['class'] = 'bdr-error'
        div.append(err_div)

    return mark_safe(ElementTree.tostring(div))
