from django.forms import ModelForm
from bdr_registry.models import Person


class PersonForm(ModelForm):

    class Meta():
        model = Person
        exclude = ('company',)

    def save(self, **kwargs):
        person = super(PersonForm, self).save(commit=False)
        person.company = self.initial['company']
        person.save()
        return person
