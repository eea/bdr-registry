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

    def setUp(self):
        self.denmark = models.Country.objects.get(name="Denmark")
        self.fgas = models.Obligation.objects.get(code='fgas')

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def test_submitted_organisation_is_saved(self):
        form_data = dict(ORG_FIXTURE, country=self.denmark.pk)
        resp = self.client.post('/organisation/add', form_data)

        self.assertEqual(models.Organisation.objects.count(), 1)
        org = models.Organisation.objects.all()[0]
        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assertEqual(org.country, self.denmark)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/organisation/%d' % org.pk)

    def prepare_form_data(self):
        form_data = {
            'organisation-country': self.denmark.pk,
            'organisation-obligation': self.fgas.pk,
        }
        for key, value in ORG_FIXTURE.items():
            form_data['organisation-' + key] = value
        for key, value in PERSON_FIXTURE.items():
            form_data['person-' + key] = value
        return form_data

    def test_submitted_organisation_and_person_are_saved(self):
        resp = self.client.post('/self_register', self.prepare_form_data())

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
        form_data = self.prepare_form_data()
        del form_data['person-email']
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Organisation.objects.count(), 0)
        self.assertEqual(resp.status_code, 200)

    def test_mail_is_sent_after_successful_self_registration(self):
        self.client.post('/self_register', self.prepare_form_data())
        self.assertEqual(len(mail.outbox), 1)


class OrganisationEditTest(TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        user_data = dict(username='test_user', password='pw')
        self.user = User.objects.create_user(**user_data)
        self.client.login(**user_data)
        self.dk = models.Country.objects.get(name="Denmark")
        org_data = dict(ORG_FIXTURE, country_id=self.dk.pk)
        self.org = models.Organisation.objects.create(**org_data)
        self.update_url = '/organisation/%d/update' % self.org.pk

    def test_model_updated_from_organisation_edit(self):
        self.user.is_superuser = True
        self.user.save()
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, name="teh new name")
        resp = self.client.post(self.update_url, org_form)
        new_org = models.Organisation.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.name, "teh new name")

    def test_modifying_obligation_or_account_is_ignored(self):
        self.user.is_superuser = True
        self.user.save()
        fgas = models.Obligation.objects.get(code='fgas')
        account = models.Account.objects.create(uid='fgas12345')
        org_form = dict(ORG_FIXTURE, country=self.dk.pk,
                        obligation=fgas.pk, account=account.pk)
        resp = self.client.post(self.update_url, org_form)
        new_org = models.Organisation.objects.get(pk=self.org.pk)
        self.assertIsNone(new_org.obligation)
        self.assertIsNone(new_org.account)

    LOGIN_PREFIX = 'http://testserver/accounts/login/?next='

    def test_organisation_account_is_allowed_to_edit(self):
        self.org.account = models.Account.objects.create(uid=self.user.username)
        self.org.save()
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, name="teh new name")
        resp = self.client.post(self.update_url, org_form)
        self.assertFalse(resp['location'].startswith(self.LOGIN_PREFIX))
        new_org = models.Organisation.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.name, "teh new name")

    def test_random_account_is_not_allowed_to_edit(self):
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, name="teh new name")
        resp = self.client.post(self.update_url, org_form)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['location'].startswith(self.LOGIN_PREFIX))


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
