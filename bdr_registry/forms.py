from captcha.fields import CaptchaField

from django.conf import settings
from django.forms.models import ModelForm, modelform_factory
from django.forms.models import ModelChoiceField

from bdr_registry import models
from bdr_management.forms.utils import set_empty_label

ORG_CREATE_EXCLUDE = ('account', 'active', 'comments')


class CompanyHDVForm(ModelForm):

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(CompanyHDVForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')

    class Meta:
        model = models.Company
        fields = ['name', 'addr_street', 'addr_place1', 'addr_postalcode', 'country', 'world_manufacturer_identifier']


class PersonHDVForm(ModelForm):

    class Meta:
        model = models.Person
        fields = ['title', 'family_name', 'first_name', 'email', 'phone']

