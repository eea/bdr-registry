from django.forms import ModelForm
from bdr_registry.models import Person


class PersonForm(ModelForm):

    class Meta():
        model = Person
        exclude = ('organisation',)

    def save(self, **kwargs):
        person = super(PersonForm, self).save(commit=False)
        person.organisation = self.initial['organisation']
        person.save()
        return person
