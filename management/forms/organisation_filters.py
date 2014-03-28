from django.forms import Form, ModelChoiceField, ChoiceField
from bdr_registry.models import Country, Obligation


class OrganisationFilters(Form):

    ACCOUNT_CHOICES = (
        ('', 'All'),
        ('0', 'Without account'),
        ('1', 'With account'),
    )

    CREATED_CHOICES = (
        ('', 'Any'),
        ('0', 'Today'),
        ('1', 'Last 7 days'),
        ('2', 'This month'),
        ('3', 'This year')
    )

    country = ModelChoiceField(queryset=Country.objects.all(),
                               empty_label='(All)')

    obligation = ModelChoiceField(queryset=Obligation.objects.all(),
                                  empty_label='(All)')

    account = ChoiceField(choices=ACCOUNT_CHOICES)

    created = ChoiceField(choices=CREATED_CHOICES)
