from django.forms import ModelForm
from bdr_management.forms.utils import set_empty_label
from bdr_registry.models import Obligation


class ObligationForm(ModelForm):

    class Meta():
        model = Obligation
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super(ObligationForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')
