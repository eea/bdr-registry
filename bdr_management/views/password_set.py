from datetime import timedelta
import hashlib
from post_office import mail
from post_office.connections import connections

import uuid


from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import generic

from bdr_management import base
from bdr_management.base import Breadcrumb
from bdr_management.forms import AccountForm, SetPasswordForm
from bdr_registry.models import Account, AccountUniqueToken


class SetPasswordMixin:
    def compose_url(self, url):
        url_paths = []
        url_paths.append(settings.BDR_SERVER_URL.strip("/"))
        url_paths.append(url.strip("/"))
        return "/".join(url_paths)

    def send_mail(self, token, person=None, company=None):
        connections.close()
        if person:
            company = person.company
            account = person.account
        elif company:
            person = company.main_reporter
            account = company.account

        if company.obligation.code == "hdv":
            sender = settings.HDV_EMAIL_FROM
        elif company.obligation.code == "hdv_resim":
            sender = settings.HDV_RESIM_EMAIL_FROM
        else:
            sender = settings.BDR_EMAIL_FROM
        context = {
            "url": self.compose_url(
                reverse("person_set_new_password", kwargs={"token": token})
            ),
            "person": person,
            "account": account,
        }
        template = render_to_string("emails/password_set_request.html", context)
        text = render_to_string("emails/password_set_request.txt", context)
        mail.send(
            recipients=[person.email],
            sender=sender,
            subject="BDR Registry password re-set",
            message=text,
            html_message=template,
            priority="now",
        )
        connections.close()

    def send_password(self, account):
        salt = uuid.uuid4().hex + account.uid
        token = hashlib.sha256(salt.encode("utf-8")).hexdigest()
        AccountUniqueToken.objects.create(token=token, account=account)
        return token


class PasswordSetRequest(SetPasswordMixin, base.ModelTableViewMixin, generic.FormView):

    template_name = "bdr_management/password_set_request.html"
    model = Account
    form_class = AccountForm

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Request password reset")),
        ]
        data = super(PasswordSetRequest, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = reverse("home")
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            account = form.cleaned_data["username"]
            token = self.send_password(account)
            if hasattr(account, "persons"):
                if account.persons.all().count() != 0:
                    email = account.persons.first().email
                    msg = _(
                        "An e-mail with a reset link has been sent to {}.".format(email)
                    )
                    self.send_mail(token, person=account.person)
            if hasattr(account, "companies"):
                if account.companies.all().count() != 0:
                    email = account.companies.first().main_reporter.email
                    msg = _(
                        "An e-mail with a reset link has been sent to the {} (the company account owner).".format(
                            email
                        )
                    )
                    self.send_mail(token, company=account.company)
            messages.success(request, msg)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("home")


class PasswordSetNewPassword(base.ModelTableViewMixin, generic.FormView):

    template_name = "bdr_management/password_set.html"
    model = Account
    form_class = SetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        token = self.kwargs["token"]
        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_later = this_hour + timedelta(hours=5)
        account_token = AccountUniqueToken.objects.filter(
            token=token, datetime__lt=one_hour_later
        )
        if not account_token:
            return HttpResponseForbidden()
        self.account = account_token.first().account
        return super(PasswordSetNewPassword, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            Breadcrumb(reverse("home"), title=_("Registry")),
            Breadcrumb("", _("Request password reset")),
        ]
        data = super(PasswordSetNewPassword, self).get_context_data(**kwargs)
        data["breadcrumbs"] = breadcrumbs
        data["cancel_url"] = reverse("home")
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save(self.account)
            tokens = AccountUniqueToken.objects.filter(account=self.account)
            tokens.delete()
            self.form_valid(form)
            request.session.modified = True
            return redirect(settings.BDR_SERVER_URL)
        else:
            return self.form_invalid(form)

    def get_success_url(self, **kwargs):
        return settings.BDR_SERVER_URL
