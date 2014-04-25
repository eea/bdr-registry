from django.forms import BooleanField, Form, ModelForm, ModelChoiceField
from bdr_registry.models import Company


class CompanyForm(ModelForm):

    class Meta():
        model = Company
        exclude = ('id',)
        empty_label = ""

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if isinstance(field, ModelChoiceField):
                field.empty_label = ''


class CompanyDeleteForm(Form):

    delete_reporting_folder = BooleanField()
    delete_account = BooleanField()
