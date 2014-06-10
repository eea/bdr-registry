from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from post_office.mail import send
from django.conf import settings
from bdr_registry.models import Account
from bdr_registry.views import valid_email


def notify_add_file(request, *args, **kwargs):

    account = get_object_or_404(Account, uid=kwargs['account'])
    company = account.company
    recipients = [p.email for p in company.people.all()
                  if valid_email(p.email)]

    send(recipients=recipients, sender=settings.BDR_EMAIL_FROM)
    return HttpResponse()


def notify_add_feedback(request, *args, **kwargs):
    account = get_object_or_404(Account, uid=kwargs['account'])
    company = account.company
    recipients = [p.email for p in company.people.all()
                  if valid_email(p.email)]

    send(recipients=recipients, sender=settings.BDR_EMAIL_FROM)
    return HttpResponse()


def notify_release(request, *args, **kwargs):
    account = get_object_or_404(Account, uid=kwargs['account'])
    company = account.company

    recipients = [u.email for u in User.objects.filter(
        Q(groups__name=settings.BDR_HELPDESK_GROUP) &
        Q(obligations__pk=company.obligation.pk))
        if valid_email(u.email)]

    send(recipients=recipients, sender=settings.BDR_EMAIL_FROM)
    return HttpResponse()