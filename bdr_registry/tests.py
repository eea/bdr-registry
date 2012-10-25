import unittest
from django.test.client import Client
from bdr_registry import models


class FormSubmitTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

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
