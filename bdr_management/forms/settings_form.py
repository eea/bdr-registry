from django.forms import ModelForm
from django.conf import settings
from bdr_management.forms import set_empty_label
from bdr_registry.models import ReportingYear, SiteConfiguration


class SettingsForm(ModelForm):

    class Meta():
        model = SiteConfiguration
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')

    def save(self, commit=True):
        config = super(SettingsForm, self).save(commit)

        for year in range(settings.FIRST_REPORTING_YEAR,
                          config.reporting_year + 1):
            ReportingYear.objects.get_or_create(year=year)

        return config
