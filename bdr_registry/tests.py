from django.test import TestCase, TransactionTestCase
from django.core import mail
from bdr_registry import models


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


class FormSubmitTest(TransactionTestCase):

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def test_submitted_organisation_is_saved(self):
        denmark = models.Country.objects.get(name="Denmark")
        form_data = dict(ORG_FIXTURE, country=denmark.pk)
        resp = self.client.post('/organisation/add', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assertEqual(org.country, denmark)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/organisation/%d' % org.pk)

    def test_submitted_organisation_and_person_are_saved(self):
        denmark = models.Country.objects.get(name="Denmark").pk
        form_data = {'organisation-country': denmark}
        for key, value in ORG_FIXTURE.items():
            form_data['organisation-' + key] = value
        for key, value in PERSON_FIXTURE.items():
            form_data['person-' + key] = value
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        person = models.Person.objects.all()[0]

        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assert_object_has_items(person, PERSON_FIXTURE)
        self.assertEqual(person.organisation, org)
        self.assertItemsEqual(org.people.all(), [person])

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/self_register/done')

    def test_invalid_person_rolls_back_saved_organisation(self):
        denmark = models.Country.objects.get(name="Denmark").pk
        form_data = {'organisation-country': denmark}
        for key, value in ORG_FIXTURE.items():
            form_data['organisation-' + key] = value
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Organisation.objects.count(), 0)

        self.assertEqual(resp.status_code, 200)

    def test_mail_is_sent_after_successful_self_registration(self):
        denmark = models.Country.objects.get(name="Denmark").pk
        form_data = {'organisation-country': denmark}
        for key, value in ORG_FIXTURE.items():
            form_data['organisation-' + key] = value
        for key, value in PERSON_FIXTURE.items():
            form_data['person-' + key] = value
        self.client.post('/self_register', form_data)

        self.assertEqual(len(mail.outbox), 1)


class ApiTest(TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        user_data = dict(username='user', password='pw')
        User.objects.create_user(**user_data)
        self.client.login(**user_data)

    def test_response_empty_when_no_organisations_in_db(self):
        resp = self.client.get('/organisation/all')
        self.assertEqual(resp['Content-Type'], 'application/xml')
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<organisations></organisations>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_single_organisation_from_db(self):
        dk = models.Country.objects.get(name="Denmark")
        kwargs = dict(ORG_FIXTURE, country=dk)
        org = models.Organisation.objects.create(**kwargs)

        resp = self.client.get('/organisation/all')
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<organisations>'
                      '<organisation>'
                        '<name>Teh company</name>'
                        '<country>Denmark</country>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<addr_place1>Copenhagen</addr_place1>'
                        '<addr_place2>Hovedstaden</addr_place2>'
                        '<pk>' + str(org.pk) + '</pk>'
                      '</organisation>'
                    '</organisations>')
        self.assertEqual(resp.content, expected)
