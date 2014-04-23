from collections import OrderedDict
from functools import wraps
import base64

from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import ModelForm, modelform_factory
from django.forms.models import ModelChoiceField
from django.db import transaction
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound)
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
import xmltodict
import models


class CanEdit(object):

    def __init__(self, organisation):
        self.organisation = organisation

    def __call__(self, user):
        if user.is_superuser:
            return True

        account = self.organisation.account
        if account is not None:
            if account.uid == user.username:
                return True

        return False


def home(request):
    return TemplateResponse(request, 'home.html', {})


ORG_CREATE_EXCLUDE = ('account', 'active', 'comments')
ORG_ADMIN_EXCLUDE = ORG_CREATE_EXCLUDE + ('obligation', 'country')


class CompanyCreate(CreateView):

    model = models.Company
    template_name = 'organisation_add.html'

    def get_form_class(self):
        return modelform_factory(models.Company,
                                 exclude=ORG_CREATE_EXCLUDE)


class CompanyUpdate(UpdateView):

    model = models.Company
    template_name = 'company_update.html'

    def get_form_class(self):
        exclude = ORG_ADMIN_EXCLUDE
        if not self.request.user.is_superuser:
            exclude = exclude + ('name',)
        return modelform_factory(models.Company, exclude=exclude)

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(CompanyUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        return reverse('company_update', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        try:
            tmpl = settings.BDR_REPORTEK_ORGANISATION_URL
            url = tmpl.format(org=self.object)
        except:
            url = None
        kwargs['reporting_url'] = url
        kwargs['helpdesk_email'] = settings.BDR_HELPDESK_EMAIL
        return super(CompanyUpdate, self).get_context_data(**kwargs)


def attempt_basic_auth(request):
    if request.user.is_authenticated():
        return
    authorization = request.META.get('HTTP_AUTHORIZATION')
    if not authorization:
        return
    authorization = authorization.lstrip('Basic ')
    username, password = base64.b64decode(authorization).split(':', 1)
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        messages.add_message(request, messages.INFO,
                             u"Logged in as %s" % user.username)


def edit_company(request):
    attempt_basic_auth(request)
    uid = request.GET.get('uid')
    if not uid:
        return HttpResponseNotFound()
    account = get_object_or_404(models.Account, uid=uid)
    org = get_object_or_404(models.Company, account=account)
    location = reverse('company', kwargs={'pk': org.pk})
    return HttpResponseRedirect(location)


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
def company_all(request):
    data = []
    account_uid = request.GET.get('account_uid')
    for organisation in models.Company.objects.all():
        if account_uid is not None:
            if (organisation.account is None or
                organisation.account.uid != account_uid):
                continue
        item = OrderedDict((k, getattr(organisation, k))
                for k in ['pk', 'name', 'addr_street', 'addr_postalcode',
                          'eori', 'vat_number', 'addr_place1',
                          'addr_place2'])
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

        def person_data(person):
            phones = [person.phone, person.phone2, person.phone3]
            return OrderedDict([
                ('name', u"{p.first_name} {p.family_name}".format(p=person)),
                ('email', person.email),
                ('phone', [p for p in phones if p]),
                ('fax', person.fax),
            ])
        item['person'] = [person_data(p) for p in organisation.people.all()]

        def comment_data(comment):
            return OrderedDict([
                ('text', comment.text),
                ('created', comment.created)
            ])
        item['comment'] = [comment_data(c) for c in organisation.comments.all()]

        data.append(item)
    xml = xmltodict.unparse({'organisations': {'organisation': data}})
    return HttpResponse(xml, content_type='application/xml')


class CompanyForm(ModelForm):

    obligation = ModelChoiceField(queryset=models.Obligation.objects,
                                  required=True)

    class Meta:
        model = models.Company
        exclude = ORG_CREATE_EXCLUDE


PersonForm = modelform_factory(models.Person, exclude=['organisation'])
CommentForm = modelform_factory(models.Comment, exclude=['organisation'])


class SelfRegister(View):

    def make_forms(self, post_data=None):
        return (CompanyForm(post_data, prefix='organisation'),
                PersonForm(post_data, prefix='person'))

    def render_forms(self, request, organisation_form,
                     person_form):
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


class CompanyAddPerson(CreateView):

    template_name = 'organisation_add_person.html'
    model = models.Person
    form_class = PersonForm

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(CompanyAddPerson, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(CompanyAddPerson, self).get_context_data(**kwargs)
        context['organisation_pk'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        person = form.save(commit=False)
        pk = self.kwargs['pk']
        person.organisation = models.Company.objects.get(pk=pk)
        person.save()
        return HttpResponseRedirect(reverse('company_update', args=[pk]))


class PersonUpdate(UpdateView):

    template_name = 'person_update.html'
    model = models.Person
    form_class = PersonForm

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Person, pk=pk).organisation
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(PersonUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        organisation = self.object.organisation
        return reverse('company_update', args=[organisation.pk])

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO,
                             u"Details saved: %s" % self.object)
        return super(PersonEdit, self).form_valid(form)


class PersonDelete(DeleteView):

    model = models.Person
    template_name = 'person_confirm_delete.html'

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Person, pk=pk).organisation
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(PersonDelete, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.organisation.people.count() == 1:
            messages.add_message(self.request, messages.ERROR,
                                 u"Can't delete last person")

        else:
            self.object.delete()
            messages.add_message(self.request, messages.INFO,
                                 u"Person deleted: %s" % self.object)

        organisation = self.object.organisation
        url = reverse('company_update', args=[organisation.pk])
        return HttpResponseRedirect(url)


class CompanyAddComment(CreateView):

    template_name = 'organisation_add_comment.html'
    model = models.Comment
    form_class = CommentForm

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(CompanyAddComment, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(CompanyAddComment, self).get_context_data(**kwargs)
        context['organisation_pk'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        comment = form.save(commit=False)
        pk = self.kwargs['pk']
        comment.organisation = models.Company.objects.get(pk=pk)
        comment.save()
        return HttpResponseRedirect(reverse('company_update', args=[pk]))


class CommentUpdate(UpdateView):

    template_name = 'comment_update.html'
    model = models.Comment
    form_class = CommentForm

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Comment, pk=pk).organisation
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(CommentUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        organisation = self.object.organisation
        return reverse('company_update', args=[organisation.pk])

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO,
                             u"Details saved: %s" % self.object)
        return super(CommentUpdate, self).form_valid(form)


class CommentDelete(DeleteView):

    model = models.Comment
    template_name = 'comment_confirm_delete.html'

    def dispatch(self, request, pk):
        organisation = get_object_or_404(models.Comment, pk=pk).organisation
        can_edit = CanEdit(organisation)
        login_url = reverse('login')
        dispatch = super(CommentDelete, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(self.request, messages.INFO,
                             u"Comment from %s successfully deleted" %
                             self.object.created.strftime('%d %B %Y'))

        organisation = self.object.organisation
        url = reverse('company_update', args=[organisation.pk])
        return HttpResponseRedirect(url)


def send_notification_email(context):
    mail_from = settings.BDR_EMAIL_FROM
    mail_to = [settings.BDR_HELPDESK_EMAIL]
    html = render_to_string('self_register_mail.html', context)
    message = mail.EmailMessage("BDR Registration", html, mail_from, mail_to)
    message.content_subtype = 'html'
    message.send(fail_silently=False)


def crashme(request):
    if request.user.is_superuser:
        raise RuntimeError("Crashing as requested")
    else:
        return HttpResponse("Must be administrator")


def ping(request):
    models.Obligation.objects.all()[0].name  # just get something from db
    return HttpResponse("bdr-registry is ok\n")


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, "You have logged out.")
    return redirect('home')
