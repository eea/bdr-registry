from django.forms import Form, ModelChoiceField
from bdr_registry.models import Country, Obligation


class OrganisationFilters(Form):
    country = ModelChoiceField(queryset=Country.objects.all(),
                               empty_label='(Nothing)')
    obligation = ModelChoiceField(queryset=Obligation.objects.all(),
                                  empty_label='(Nothing)')
