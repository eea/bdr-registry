from bdr_management.forms.utils import set_empty_label
from django.forms import BooleanField, Form, ModelForm
from bdr_registry.models import Company


class CompanyForm(ModelForm):
    class Meta():
        model = Company
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        obligations = kwargs.pop('obligations', [])
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['obligation'].queryset = (
            self.fields['obligation'].queryset.
            filter(pk__in=obligations))
        if self.instance and self.instance.id:
            self.fields['obligation'].required = False
            self.fields['obligation'].widget.attrs['disabled'] = 'disabled'
        set_empty_label(self.fields, '')

    def clean_obligation(self):
        if self.instance and self.instance.id:
            return self.instance.obligation
        return self.cleaned_data['obligation']


class CompanyDeleteForm(Form):
    delete_reporting_folder = BooleanField()
    delete_account = BooleanField()
