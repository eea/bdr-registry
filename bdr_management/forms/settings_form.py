from django.forms import Form, IntegerField
from django.utils.translation import ugettext as _
import django_settings


class SettingsForm(Form):

    reporting_year = IntegerField(label=_('Reporting year'))

    def is_valid(self):
        valid = super(SettingsForm, self).is_valid()
        if valid:
            django_settings.set('Integer', 'reporting_year',
                                self.cleaned_data['reporting_year'])
        return valid
