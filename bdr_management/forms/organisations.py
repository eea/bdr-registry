from django.forms import BooleanField, Form, ModelForm
from bdr_registry.models import Company


class OrganisationForm(ModelForm):

    class Meta():
        model = Company
        exclude = ('id',)


class OrganisationDeleteForm(Form):

    delete_reporting_folder = BooleanField()
    delete_account = BooleanField()
