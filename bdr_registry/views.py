from django.views.generic import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect
from django.forms.models import modelform_factory
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
        PersonForm = modelform_factory(models.Person)
        return (OrganisationForm(post_data, prefix='organisation'),
                PersonForm(post_data, prefix='person'))

    def get(self, request):
        organisation_form, person_form = self.make_forms()
        return render(request, 'self_register.html', {
            'organisation_form': organisation_form,
            'person_form': person_form,
        })

    def post(self, request):
        organisation_form, person_form = self.make_forms(request.POST)

        if organisation_form.is_valid():
            organisation = organisation_form.save()
            person_form.data['person-organisation'] = organisation.pk

            if person_form.is_valid():
                person_form.save()
                return redirect('self_register_done')

            else:
                raise NotImplementedError

        else:
            raise NotImplementedError
