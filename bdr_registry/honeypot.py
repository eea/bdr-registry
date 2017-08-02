from datetime import datetime
from django.conf import settings


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
