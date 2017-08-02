from django.core.exceptions import ValidationError
from django.core.validators import validate_email

try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict
import base64
from django.contrib.auth.models import User
from django.db.models import Q

from django.views.generic import View, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import ModelForm, modelform_factory
from django.forms.models import ModelChoiceField
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from honeypot.decorators import check_honeypot

from post_office.mail import send

from bdr_registry import models
from bdr_management.forms.utils import set_empty_label


class CanEdit(object):

    def __init__(self, company):
        self.company = company

    def __call__(self, user):
        if user.is_superuser:
            return True

        account = self.company.account
        if account is not None:
            if account.uid == user.username:
                return True

        return False


class home(TemplateView):

    template_name = 'home.html'

    def get_user_company_details(self):
        info = {
            'has_company': False,
            'company': None,
            'has_reporting_folder': False,
            'reporting_folder_path': None
        }
        try:
            account = models.Account.objects.get(uid=self.request.user)
        except models.Account.DoesNotExist:
            pass
        else:
            try:
                company = models.Company.objects.get(account=account)
            except models.Company.DoesNotExist:
                pass
            else:
                info['has_company'] = True
                info['company'] = company
                info['reporting_folder_path'] = \
                    company.build_reporting_folder_path()
                info['has_reporting_folder'] = \
                    company.has_reporting_folder(info['reporting_folder_path'])
        return info

ORG_CREATE_EXCLUDE = ('account', 'active', 'comments')
ORG_ADMIN_EXCLUDE = ORG_CREATE_EXCLUDE + ('obligation', 'country')


class CompanyCreate(CreateView):

    model = models.Company
    template_name = 'company_add.html'

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
        company = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(company)
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


class CompanyForm(ModelForm):

    obligation = ModelChoiceField(
        queryset=models.Obligation.objects.exclude(code__in=settings.SELF_OBL_EXCLUDE),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')

    class Meta:
        model = models.Company
        exclude = ORG_CREATE_EXCLUDE


PersonForm = modelform_factory(models.Person, exclude=['company'])
CommentForm = modelform_factory(models.Comment, exclude=['company'])


class SelfRegister(View):

    @method_decorator(check_honeypot)
    def dispatch(self, request, *args, **kwargs):
        return super(SelfRegister, self).dispatch(request, *args, **kwargs)

    def make_forms(self, post_data=None):
        return (CompanyForm(post_data, prefix='company'),
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
        company_form, person_form = self.make_forms(request.POST.dict())

        if company_form.is_valid() and person_form.is_valid():
            company = company_form.save()
            person = person_form.save(commit=False)
            person.company = company
            person.save()

            send_notification_email({
                'company': company,
                'person': person,
            })

            return redirect('self_register_done')

        return self.render_forms(request, company_form, person_form)


class CompanyAddPerson(CreateView):

    template_name = 'company_add_person.html'
    model = models.Person
    form_class = PersonForm

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(company)
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
        person.company = models.Company.objects.get(pk=pk)
        person.save()
        return HttpResponseRedirect(reverse('company_update', args=[pk]))


class PersonUpdate(UpdateView):

    template_name = 'person_update.html'
    model = models.Person
    form_class = PersonForm

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Person, pk=pk).company
        can_edit = CanEdit(company)
        login_url = reverse('login')
        dispatch = super(PersonUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        company = self.object.company
        return reverse('company_update', args=[company.pk])

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO,
                             u"Details saved: %s" % self.object)
        return super(PersonUpdate, self).form_valid(form)


class PersonDelete(DeleteView):

    model = models.Person
    template_name = 'person_confirm_delete.html'

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Person, pk=pk).company
        can_edit = CanEdit(company)
        login_url = reverse('login')
        dispatch = super(PersonDelete, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.company.people.count() == 1:
            messages.add_message(self.request, messages.ERROR,
                                 u"Can't delete last person")

        else:
            self.object.delete()
            messages.add_message(self.request, messages.INFO,
                                 u"Person deleted: %s" % self.object)

        company = self.object.company
        url = reverse('company_update', args=[company.pk])
        return HttpResponseRedirect(url)


class CompanyAddComment(CreateView):

    template_name = 'organisation_add_comment.html'
    model = models.Comment
    form_class = CommentForm

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Company, pk=pk)
        can_edit = CanEdit(company)
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
        comment.company = models.Company.objects.get(pk=pk)
        comment.save()
        return HttpResponseRedirect(reverse('company_update', args=[pk]))


class CommentUpdate(UpdateView):

    template_name = 'comment_update.html'
    model = models.Comment
    form_class = CommentForm

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Comment, pk=pk).company
        can_edit = CanEdit(company)
        login_url = reverse('login')
        dispatch = super(CommentUpdate, self).dispatch
        wrapped_dispatch = user_passes_test(can_edit, login_url)(dispatch)
        return wrapped_dispatch(request, pk=pk)

    def get_success_url(self):
        company = self.object.company
        return reverse('company_update', args=[company.pk])

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO,
                             u"Details saved: %s" % self.object)
        return super(CommentUpdate, self).form_valid(form)


class CommentDelete(DeleteView):

    model = models.Comment
    template_name = 'comment_confirm_delete.html'

    def dispatch(self, request, pk):
        company = get_object_or_404(models.Comment, pk=pk).company
        can_edit = CanEdit(company)
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

        company = self.object.company
        url = reverse('company_update', args=[company.pk])
        return HttpResponseRedirect(url)


def valid_email(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def send_notification_email(context):

    company = context.get('company')

    recipients = [u.email for u in User.objects.filter(
        Q(groups__name=settings.BDR_HELPDESK_GROUP) &
        Q(obligations__pk=company.obligation.pk))
        if valid_email(u.email)]

    config = models.SiteConfiguration.objects.get()
    template = config.self_register_email_template

    send(recipients=recipients, sender=settings.BDR_EMAIL_FROM,
         template=template, context=context, priority='now')


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
