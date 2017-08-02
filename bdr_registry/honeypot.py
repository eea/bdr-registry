from datetime import datetime
from functools import wraps

import six
from django.conf import settings
from django.http import Http404
from django.utils.decorators import available_attrs


def honey_pot_value():
    """
        Generate honeypot field value according to settings.HONEYPOT_FORMAT
    """
    return datetime.now().strftime(settings.HONEYPOT_FORMAT)


def honey_pot_checker(value):
    """
        Verify that value is a valid honeypot.

        Ensures that the field respects format and was not evaluated more than one
        hour ago.
    """
    current_data = datetime.now()
    try:
        delta = current_data - datetime.strptime(value, settings.HONEYPOT_FORMAT)
    except ValueError:
        return False
    return delta.seconds / 3600 < 1


def verify_honeypot_value(request):
    """
        Verify that request.POST[settings.HONEYPOT_FIELD_NAME] is a valid honeypot.
        Otherwise raise Http404.

        Ensures that the field exists and passes verification according to
        honey_pot_checker.
    """
    if request.method == 'POST':
        field = settings.HONEYPOT_FIELD_NAME
        if field not in request.POST or not honey_pot_checker(request.POST[field]):
            raise Http404


def custom_check_honeypot(func=None):
    """
        Custom check request.POST for valid honeypot field.

    """
    def decorated(func):
        def inner(request, *args, **kwargs):
            response = verify_honeypot_value(request)
            if response:
                return response
            else:
                return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)

    if func is None:
        def decorator(func):
            return decorated(func)
        return decorator
    return decorated(func)
