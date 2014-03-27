from django.forms import Form, ModelChoiceField, ChoiceField
from bdr_registry.models import Country, Obligation


class OrganisationFilters(Form):

    ACCOUNT_CHOICES = (
        ('', 'All'),
        ('0', 'Without account'),
        ('1', 'With account'),
    )

    country = ModelChoiceField(queryset=Country.objects.all(),
                               empty_label='(All)')

    obligation = ModelChoiceField(queryset=Obligation.objects.all(),
                                  empty_label='(All)')

    account = ChoiceField(choices=ACCOUNT_CHOICES)
