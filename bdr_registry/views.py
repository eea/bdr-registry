from collections import OrderedDict
from functools import wraps
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect
from django.forms.models import ModelForm, modelform_factory
from django.forms.models import ModelChoiceField
from django.db import transaction
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
import xmltodict
import models


class OrganisationCreate(CreateView):

    model = models.Organisation
    template_name = 'organisation_add.html'


class OrganisationUpdate(UpdateView):

    model = models.Organisation
    template_name = 'organisation_update.html'
    form_class = modelform_factory(models.Organisation,
                                   exclude=['obligation', 'account'])

    def dispatch(self, request, pk):
        def can_edit(user):
            if user.is_superuser:
                return True

            account = models.Organisation.objects.get(pk=pk).account
            if account is not None:
                if account.uid == user.username:
                    return True

            return False

        login_url = reverse('login')
        dispatch = super(OrganisationUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        return reverse('organisation_update', args=[self.object.pk])


class Organisation(DetailView):

    model = models.Organisation
    template_name = 'organisation.html'


def api_key_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        apikey = request.GET.get('apikey', '')
        if models.ApiKey.objects.filter(key=apikey).count() < 1:
            return HttpResponseForbidden(
                "Invalid API key, please set correct 'apikey' GET parameter.")
        return view(request, *args, **kwargs)
    return wrapper


@api_key_required
def organisation_all(request):
    data = []
    account_uid = request.GET.get('account_uid')
    for organisation in models.Organisation.objects.all():
        if account_uid is not None:
            if (organisation.account is None or
                organisation.account.uid != account_uid):
                continue
        item = OrderedDict((k, getattr(organisation, k))
                for k in ['pk', 'name', 'addr_street', 'addr_postalcode',
                          'addr_place1', 'addr_place2'])
        if organisation.account is not None:
            item['account'] = organisation.account.uid
        if organisation.obligation is not None:
            item['obligation'] = {
                '@name': organisation.obligation.name,
                '#text': organisation.obligation.code,
            }
        item['country'] = {
            '@name': organisation.country.name,
            '#text': organisation.country.code,
        }
        item['person'] = [OrderedDict([
                ('name', u"{p.first_name} {p.family_name}".format(p=person)),
                ('email', person.email),
                ('phone', person.phone),
                ('fax', person.fax),
            ]) for person in organisation.people.all()]
        data.append(item)
    xml = xmltodict.unparse({'organisations': {'organisation': data}})
    return HttpResponse(xml, content_type='application/xml')


class OrganisationForm(ModelForm):

    obligation = ModelChoiceField(queryset=models.Obligation.objects,
                                  required=True)

    class Meta:
        model = models.Organisation
        exclude = ['account']


PersonForm = modelform_factory(models.Person, exclude=['organisation'])


class SelfRegister(View):

    def make_forms(self, post_data=None):
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
