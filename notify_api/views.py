from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import View
from post_office.mail import send
from bdr_registry.models import Account, SiteConfiguration, ApiKey
from bdr_registry.views import valid_email


class AddFile(View):

    def post(self, request, *args, **kwargs):

        api_key = request.POST.get('apiKey', '')
        if api_key is None:
            return HttpResponseForbidden()

        try:
            ApiKey.objects.get(key=api_key)
        except ObjectDoesNotExist:
            return HttpResponseForbidden()

        account = get_object_or_404(Account, uid=kwargs['account'])
        company = account.company
        recipients = [p.email for p in company.people.all()
                      if valid_email(p.email)]

        conf = SiteConfiguration.objects.get()
        template = conf.notify_add_file_template
        send(recipients=recipients, sender=settings.BDR_EMAIL_FROM,
             template=template)
        return HttpResponse()