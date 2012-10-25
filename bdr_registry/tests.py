from django.test.client import Client
from django.test import TestCase
from bdr_registry import models


class FormSubmitTest(TestCase):

    ORG_FIXTURE = {
        'name': "Teh company",
        'addr_street': "teh street",
        'addr_place1': "Copenhagen",
        'addr_postalcode': "123456",
        'addr_place2': "Hovedstaden",
    }

    PERSON_FIXTURE = {
        'title': "Mr.",
        'first_name': "Joe",
        'family_name': "Tester",
        'email': "tester@example.com",
        'phone': "555 1234",
    }

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def test_submitted_organisation_is_saved(self):
        denmark = models.Country.objects.get(name="Denmark")
        form_data = dict(self.ORG_FIXTURE, country=denmark.pk)
        resp = self.client.post('/organisation/add', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        self.assert_object_has_items(org, self.ORG_FIXTURE)
        self.assertEqual(org.country, denmark)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/organisation/%d' % org.pk)

    def test_submitted_organisation_and_person_are_saved(self):
        denmark = models.Country.objects.get(name="Denmark").pk
        form_data = {'organisation-country': denmark}
        for key, value in self.ORG_FIXTURE.items():
            form_data['organisation-' + key] = value
        for key, value in self.PERSON_FIXTURE.items():
            form_data['person-' + key] = value
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        person = models.Person.objects.all()[0]

        self.assert_object_has_items(org, self.ORG_FIXTURE)
        self.assert_object_has_items(person, self.PERSON_FIXTURE)
        self.assertEqual(person.organisation, org)
        self.assertItemsEqual(org.people.all(), [person])

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/self_register/done')
