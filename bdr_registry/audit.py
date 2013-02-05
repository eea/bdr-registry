""" Audit logging """

import logging
from django.conf import settings
import local

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def log(message, *args, **kwargs):
    request = local.get_request()
    kwargs.setdefault('extra', {}).update({
        'request_username': request.user.username,
        'request_ip': request.META['REMOTE_ADDR'],
    })
    logger.info(message, *args, **kwargs)


def _configure_handler():
    audit_format = ("%(asctime)s %(message)s "
                    "(username: %(request_username)s, ip: %(request_ip)s)")
    if settings.BDR_AUDIT_LOG_FILE:
        audit_handler = logging.FileHandler(settings.BDR_AUDIT_LOG_FILE)
        audit_handler.setFormatter(logging.Formatter(audit_format))
        logger.addHandler(audit_handler)


_configure_handler()
