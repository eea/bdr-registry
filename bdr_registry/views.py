from django.views.generic import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect
from django.forms.models import modelform_factory
from django.db import transaction
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
import models


class OrganisationCreate(CreateView):

    model = models.Organisation
    template_name = 'organisation_add.html'


class Organisation(DetailView):

    model = models.Organisation
    template_name = 'organisation.html'


class SelfRegister(View):

    def make_forms(self, post_data=None):
        OrganisationForm = modelform_factory(models.Organisation)
        PersonForm = modelform_factory(models.Person,
                                       exclude=('organisation',))
        return (OrganisationForm(post_data, prefix='organisation'),
                PersonForm(post_data, prefix='person'))

    def render_forms(self, request, organisation_form, person_form):
        return render(request, 'self_register.html', {
            'organisation_form': organisation_form,
            'person_form': person_form,
        })

    def get(self, request):
        return self.render_forms(request, *self.make_forms())

    def post(self, request):
        organisation_form, person_form = self.make_forms(request.POST.dict())

        if organisation_form.is_valid():
            organisation = organisation_form.save()

            if person_form.is_valid():
                person = person_form.save(commit=False)
                person.organisation = organisation
                person.save()

                send_notification_email({
                    'organisation': organisation,
                    'person': person,
                })

                return redirect('self_register_done')

            else:
                transaction.rollback()

        return self.render_forms(request, organisation_form, person_form)


def send_notification_email(context):
    mail_from = settings.BDR_EMAIL_FROM
    mail_to = [settings.BDR_ADMIN_EMAIL]
    html = render_to_string('self_register_mail.html', context)
    message = mail.EmailMessage("BDR Registration", html, mail_from, mail_to)
    message.content_subtype = 'html'
    message.send(fail_silently=False)


def crashme(request):
    if request.user.is_superuser:
        raise RuntimeError("Crashing as requested")
    else:
        return HttpResponse("Must be administrator")
