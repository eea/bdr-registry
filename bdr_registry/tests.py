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
        self.apikey = models.ApiKey.objects.create().key

    def test_response_empty_when_no_organisations_in_db(self):
        resp = self.client.get('/organisation/all?apikey=' + self.apikey)
        self.assertEqual(resp['Content-Type'], 'application/xml')
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<organisations></organisations>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_single_organisation_from_db(self):
        dk = models.Country.objects.get(name="Denmark")
        fgas = models.Obligation.objects.get(code='fgas')
        account = models.Account.objects.create(uid='fgas12345')
        kwargs = dict(ORG_FIXTURE, country=dk,
                      account=account, obligation=fgas)
        org = models.Organisation.objects.create(**kwargs)
        person = models.Person.objects.create(organisation=org,
                                              first_name="Joe",
                                              family_name="Smith",
                                              email="joe.smith@example.com",
                                              phone="555 1234",
                                              fax="555 6789")

        resp = self.client.get('/organisation/all?apikey=' + self.apikey)
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<organisations>'
                      '<organisation>'
                        '<pk>' + str(org.pk) + '</pk>'
                        '<name>Teh company</name>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<addr_place1>Copenhagen</addr_place1>'
                        '<addr_place2>Hovedstaden</addr_place2>'
                        '<account>fgas12345</account>'
                        '<obligation name="F-gases">fgas</obligation>'
                        '<country name="Denmark">dk</country>'
                        '<person>'
                          '<name>Joe Smith</name>'
                          '<email>joe.smith@example.com</email>'
                          '<phone>555 1234</phone>'
                          '<fax>555 6789</fax>'
                        '</person>'
                      '</organisation>'
                    '</organisations>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_organisation_with_matching_uid(self):
        dk = models.Country.objects.get(name="Denmark")
        fgas = models.Obligation.objects.get(code='fgas')
        kwargs = dict(ORG_FIXTURE, country=dk, obligation=fgas)
        account1 = models.Account.objects.create(uid='fgas0001')
        account2 = models.Account.objects.create(uid='fgas0002')
        org1 = models.Organisation.objects.create(account=account1, **kwargs)
        org2 = models.Organisation.objects.create(account=account2, **kwargs)

        resp = self.client.get('/organisation/all'
                               '?account_uid=fgas0002'
                               '&apikey=' + self.apikey)
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<organisations>'
                      '<organisation>'
                        '<pk>' + str(org2.pk) + '</pk>'
                        '<name>Teh company</name>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<addr_place1>Copenhagen</addr_place1>'
                        '<addr_place2>Hovedstaden</addr_place2>'
                        '<account>fgas0002</account>'
                        '<obligation name="F-gases">fgas</obligation>'
                        '<country name="Denmark">dk</country>'
                      '</organisation>'
                    '</organisations>')
        self.assertEqual(resp.content, expected)

    def test_requests_with_no_api_key_are_rejected(self):
        resp = self.client.get('/organisation/all')
        self.assertEqual(resp.status_code, 403)
