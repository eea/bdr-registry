from django.conf import settings

def settings_context(request):
    return {'debug': settings.DEBUG}
