from django.forms import ModelForm

from bdr_management.forms.utils import set_empty_label
from bdr_registry.models import EmailTemplate


class EmailTemplateForm(ModelForm):

    class Meta():
        model = EmailTemplate
        fields = ('name', 'subject', 'html_content')

    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')
