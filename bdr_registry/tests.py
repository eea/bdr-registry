from django.test.client import Client
from django.test import TestCase
from bdr_registry import models


class FormSubmitTest(TestCase):

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def test_submitted_organisation_is_saved(self):
        org_text_data = {
            'name': "Teh company",
            'addr_street': "teh street",
            'addr_place1': "Copenhagen",
            'addr_postalcode': "123456",
            'addr_place2': "Hovedstaden",
        }
        denmark = models.Country.objects.get(name="Denmark")
        resp = self.client.post('/organisation/add', dict(org_text_data, **{
            'country': denmark.pk,
        }))

        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        self.assert_object_has_items(org, org_text_data)
        self.assertEqual(org.country, denmark)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/organisation/%d' % org.pk)

    def test_submitted_organisation_and_person_are_saved(self):
        org_text_data = {
            'name': "Teh company",
            'addr_street': "teh street",
            'addr_place1': "Copenhagen",
            'addr_postalcode': "123456",
            'addr_place2': "Hovedstaden",
        }
        person_text_data = {
            'title': "Mr.",
            'first_name': "Joe",
            'family_name': "Tester",
            'email': "tester@example.com",
            'phone': "555 1234",
        }
        form_data = {
            'organisation-country': models.Country.objects.get(name="Denmark").pk,
        }
        for key, value in org_text_data.items():
            form_data['organisation-' + key] = value
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]

        self.assert_object_has_items(org, org_text_data)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/self_register/done')
