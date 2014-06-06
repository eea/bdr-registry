from django.forms import ModelForm
from bdr_management.forms.utils import set_empty_label
from bdr_registry.models import Person


class PersonForm(ModelForm):

    class Meta():
        model = Person
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        set_empty_label(self.fields, '')


class PersonFormWithoutCompany(ModelForm):

    class Meta():
        model = Person
        exclude = ('id', 'company',)

    def save(self, **kwargs):
        person = super(PersonFormWithoutCompany, self).save(commit=False)
        person.company = self.initial['company']
        person.save()
        return person
