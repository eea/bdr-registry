import unittest
from django.test.client import Client
from bdr_registry import models


class FormSubmitTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_submitted_organisation_is_saved(self):
        org_text_data = {
            'name': "Teh company",
            'addr_street': "teh street",
            'addr_place1': "Copenhagen",
            'addr_postalcode': "123456",
            'addr_place2': "Hovedstaden",
        }
        resp = self.client.post('/organisation/add', dict(org_text_data, **{
            'country': models.Country.objects.get(name="Denmark").pk,
        }))
        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        for key in org_text_data:
            self.assertEqual(getattr(org, key), org_text_data[key])
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/organisation/%d' % org.pk)
