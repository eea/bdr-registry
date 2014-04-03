from django.forms import ModelForm
from bdr_registry.models import Organisation


class OrganisationForm(ModelForm):

    class Meta():
        model = Organisation
        exclude = ('id',)
