from django.conf import settings


def settings_context(request):
    return {
        'debug': settings.DEBUG,
        'BDR_SERVER_URL': settings.BDR_SERVER_URL,
    }
