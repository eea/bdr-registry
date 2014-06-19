from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import View
from post_office.mail import send
from bdr_registry.models import Account, SiteConfiguration, ApiKey
from bdr_registry.views import valid_email


def notify(api_key, account, event):

        conf = SiteConfiguration.objects.get()
        templates = {
            'add_file': conf.notify_add_file_template,
            'add_feedback': conf.notify_add_feedback_template,
            'release': conf.notify_release_template
        }

        if api_key is None:
            return HttpResponseForbidden()
        try:
            ApiKey.objects.get(key=api_key)
        except ObjectDoesNotExist:
            return HttpResponseForbidden()
        account = get_object_or_404(Account, uid=account)
        company = account.company

        if event == 'release':
            bdr_group = Group.objects.get(name=settings.BDR_HELPDESK_GROUP)

            recipients = [
                u.email for u in bdr_group.user_set.filter(
                    obligations__pk=company.obligation.pk)
                if valid_email(u.email)
            ]
        else:
            recipients = [p.email for p in company.people.all()
                          if valid_email(p.email)]

        template = templates[event]
        send(recipients=recipients, sender=settings.BDR_EMAIL_FROM,
             template=template, context=company, priority='now')
        return HttpResponse()


class AddFile(View):

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'add_file')


class AddFeedback(View):

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'add_feedback')


class Release(View):

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'release')