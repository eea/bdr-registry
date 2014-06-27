import json
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from post_office.mail import send
from bdr_registry.models import Account, SiteConfiguration, ApiKey
from bdr_registry.views import valid_email


def notify(api_key, account_uid, event):

        conf = SiteConfiguration.objects.get()
        templates = {
            'add_file': conf.notify_add_file_template,
            'add_feedback': conf.notify_add_feedback_template,
            'release': conf.notify_release_template
        }

        if api_key is None:
            return HttpResponseForbidden(
                content=json.dumps({
                    'status': 'failed',
                    'data': {
                        'apiKey': "API key is required."
                    }
                }),
                content_type='application/json'
            )
        try:
            ApiKey.objects.get(key=api_key)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(
                content=json.dumps({
                    'status': 'fails',
                    'data': {
                        'apiKey': "Invalid API key."
                    }
                }),
                content_type='application/json'
            )
        try:
            account = Account.objects.get(uid=account_uid)
        except Account.DoesNotExist:
            return HttpResponseNotFound(
                content=json.dumps({
                    'status': 'fail',
                    'data': {
                        'account': "Account %s does not exist" % account_uid
                    }}),
                content_type='application/json'
            )
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
             template=template, context={'company': company}, priority='now')
        return HttpResponse(
            content=json.dumps({
                'status': 'success',
                'data': None
            }),
            content_type='application/json'
        )


class AddFile(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddFile, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'add_file')


class AddFeedback(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddFeedback, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'add_feedback')


class Release(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(Release, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        account = kwargs['account']
        api_key = request.POST.get('apiKey')

        return notify(api_key, account, 'release')
