from django.views.generic import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect
import models


class OrganisationCreate(CreateView):

    model = models.Organisation
    template_name = 'organisation_add.html'


class Organisation(DetailView):

    model = models.Organisation
    template_name = 'organisation.html'


class SelfRegister(View):

    def get(self, request):
        organisation_form = models.SelfRegisterOrganisationForm()
        return render(request, 'self_register.html', {
            'organisation_form': organisation_form,
        })

    def post(self, request):
        organisation_form = models.SelfRegisterOrganisationForm(request.POST)
        if organisation_form.is_valid():
            organisation_form.save()
            return redirect('self_register_done')
        else:
            raise NotImplementedError
