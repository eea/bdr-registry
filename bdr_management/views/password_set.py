from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.views import generic
import uuid, hashlib
from django.template.loader import render_to_string
from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_management.forms import AccountForm, SetPasswordForm
from bdr_registry.models import Account, Company, Person, User, AccountUniqueToken
from post_office import mail
from datetime import timedelta
from django.utils import timezone

class SetPasswordMixin:

    def compose_url(self, url):
        url_paths = []
        url_paths.append(settings.BDR_SERVER_URL.strip('/'))
        url_paths.append(url.strip('/'))
        return "/".join(url_paths)

    def send_mail(self, person, token):
        if person.company.obligation.code == 'hdv':
            sender = settings.HDV_EMAIL_FROM
        else:
            sender = settings.BDR_EMAIL_FROM
        context={
            'url': self.compose_url(reverse('person_set_new_password', kwargs={'token': token})),
            'person': person,
            'account': person.account
        }
        template = render_to_string('emails/password_set_request.html',
                                    context)
        text = render_to_string('emails/password_set_request.txt',
                                context)
        mail.send(recipients=[person.email],
                  sender=sender,
                  subject='BDR Registry password set',
                  message=text,
                  html_message=template,
                  priority='now')

    def send_password(self, account):
        salt = uuid.uuid4().hex + account.uid
        token = hashlib.sha256(salt.encode('utf-8')).hexdigest()
        AccountUniqueToken.objects.create(token=token, account=account)
        return token

class PasswordSetRequest(SetPasswordMixin, base.ModelTableViewMixin,
                     generic.FormView):

    template_name = 'bdr_management/password_set_request.html'
    model = Account
    form_class = AccountForm

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _(u'Request password reset'))
        ]
        data = super(PasswordSetRequest, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = reverse('home')
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            account = form.cleaned_data['username']
            email = account.person.email
            token = self.send_password(account)
            self.send_mail(account.person, token)
            msg = _('An e-mail with a reset link has been sent.')
            messages.success(request, msg)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('home')


class PasswordSetNewPassword(base.ModelTableViewMixin,
                     generic.FormView):

    template_name = 'bdr_management/password_set.html'
    model = Account
    form_class = SetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        token= self.kwargs['token']
        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_later = this_hour + timedelta(hours=5)
        account_token = AccountUniqueToken.objects.filter(token=token,
                                                          datetime__lt=one_hour_later)
        if not account_token:
            return HttpResponseForbidden()
        self.account = account_token.first().account
        return super(PasswordSetNewPassword, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse('home'), title=_('Registry')),
            Breadcrumb('', _(u'Request password reset'))
        ]
        data = super(PasswordSetNewPassword, self).get_context_data(**kwargs)
        data['breadcrumbs'] = breadcrumbs
        data['cancel_url'] = reverse('home')
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save(self.account)
            msg = _('Password changed succesfully.')
            messages.success(request, msg)
            tokens = AccountUniqueToken.objects.filter(account=self.account)
            tokens.delete()
            self.form_valid(form)
            return redirect(settings.BDR_SERVER_URL)
        else:
            return self.form_invalid(form)

    def get_success_url(self, **kwargs):
        return settings.BDR_SERVER_URL
