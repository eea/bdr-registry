from django.forms import Form, IntegerField
from django.utils.translation import ugettext as _
from django.conf import settings
import django_settings
from bdr_registry.models import ReportingYear


class SettingsForm(Form):

    reporting_year = IntegerField(label=_('Reporting year'))

    def is_valid(self):
        valid = super(SettingsForm, self).is_valid()
        if valid:
            selected_year = self.cleaned_data['reporting_year']
            django_settings.set('Integer', 'Reporting year',
                                selected_year)

            for year in range(settings.FIRST_REPORTING_YEAR, selected_year + 1):
                ReportingYear.objects.get_or_create(year=year)

        return valid
