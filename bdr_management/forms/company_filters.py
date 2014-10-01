from django.forms import Form, ModelChoiceField, ChoiceField
from bdr_registry.models import Country, Obligation


class CompanyFilters(Form):

    WITHOUT_ACCOUNT = 'without-account'
    WITH_ACCOUNT = 'with-account'

    ACCOUNT_CHOICES = (
        ('', 'All'),
        (WITHOUT_ACCOUNT, 'Without account'),
        (WITH_ACCOUNT, 'With account'),
    )

    TODAY = 'today'
    LAST_7_DAYS = 'last-7-days'
    THIS_MONTH = 'this-month'
    THIS_YEAR = 'this-year'

    CREATED_CHOICES = (
        ('', 'Any'),
        (TODAY, 'Today'),
        (LAST_7_DAYS, 'Last 7 days'),
        (THIS_MONTH, 'This month'),
        (THIS_YEAR, 'This year')
    )

    country = ModelChoiceField(queryset=Country.objects.all(),
                               empty_label='All')

    obligation = ModelChoiceField(
        queryset=Obligation.objects.all(),
        empty_label='All')

    account = ChoiceField(choices=ACCOUNT_CHOICES)

    created = ChoiceField(choices=CREATED_CHOICES)

    def __init__(self, *args, **kwargs):
        obligations = kwargs.pop('obligations', [])
        super(CompanyFilters, self).__init__(*args, **kwargs)
        self.fields['obligation'].queryset = (
                        self.fields['obligation'].queryset.
                        filter(pk__in=obligations))
