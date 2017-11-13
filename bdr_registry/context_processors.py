from django.conf import settings
from getenv import env


def settings_context(request):
    return {
        'debug': settings.DEBUG,
        'BDR_SERVER_URL': settings.BDR_SERVER_URL,
    }


def sentry(request):
    sentry_id = ''
    if hasattr(request, 'sentry'):
        sentry_id = request.sentry['id']
    return {
        'sentry_id': sentry_id,
        'sentry_public_id': env('SENTRY_PUBLIC_DSN', ''),
    }
