import logging
from contextlib import contextmanager

from django.test import TestCase, TransactionTestCase
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.admin import helpers
from bdr_registry import models
from mock import patch


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

COMMENT_FIXTURE = {
    'text': "This is a comment"
}

OBLIGATON_CODE = "fgas"

LOGIN_PREFIX = 'http://testserver/accounts/login/?next='


def create_user_and_login(client,
                          username='test_user', password='pw',
                          staff=False, superuser=False):
    user_data = dict(username=username, password=password)
    user = User.objects.create_user(**user_data)
    user.is_superuser = superuser
    user.is_staff = staff
    user.save()
    with patch('django_auth_ldap.config._LDAPConfig.ldap') as p:
        client.login(**user_data)
    return user


@contextmanager
def quiet_request_logging():
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(previous_level)


class FormSubmitTest(TransactionTestCase):

    def setUp(self):
        self.denmark = models.Country.objects.get(name="Denmark")
        self.fgas = models.Obligation.objects.get(code='fgas')

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def prepare_form_data(self):
        form_data = {
            'company-country': self.denmark.pk,
            'company-obligation': self.fgas.pk,
        }
        for key, value in ORG_FIXTURE.items():
            form_data['company-' + key] = value
        for key, value in PERSON_FIXTURE.items():
            form_data['person-' + key] = value
        for key, value in COMMENT_FIXTURE.items():
            form_data['comment-' + key] = value
        return form_data

    def test_submitted_company_and_person_are_saved(self):
        resp = self.client.post('/self_register', self.prepare_form_data())

        self.assertEqual(models.Company.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        org = models.Company.objects.all()[0]
        person = models.Person.objects.all()[0]

        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assert_object_has_items(person, PERSON_FIXTURE)
        self.assertEqual(person.company, org)
        self.assertItemsEqual(org.people.all(), [person])

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/self_register/done')

    def test_invalid_person_rolls_back_saved_company(self):
        form_data = self.prepare_form_data()
        del form_data['person-email']
        resp = self.client.post('/self_register', form_data)

        self.assertEqual(models.Company.objects.count(), 0)
        self.assertEqual(resp.status_code, 200)

    def test_mail_is_sent_after_successful_self_registration(self):
        self.client.post('/self_register', self.prepare_form_data())
        self.assertEqual(len(mail.outbox), 1)


class CompanyPasswordTest(TestCase):

    def setUp(self):
        self.dk = models.Country.objects.get(name="Denmark")
        self.fgas = models.Obligation.objects.get(code='fgas')
        self.account = models.Account.objects.create_for_obligation(self.fgas)
        self.account.set_random_password()
        self.acme = models.Company.objects.create(country=self.dk,
                                                  obligation=self.fgas,
                                                  account=self.account)
        ldap_editor_patch = patch('bdr_registry.admin.create_ldap_editor')
        ldap_editor_patch.start()
        self.addCleanup(ldap_editor_patch.stop)

    def test_password_reset_changes_password(self):
        password = self.account.password
        create_user_and_login(self.client, superuser=True, staff=True)
        self.client.post('/admin/bdr_registry/company/', {
            helpers.ACTION_CHECKBOX_NAME: self.acme.pk,
            'action': 'reset_password',
            'perform_reset': 'yes',
        })

        new_password = models.Account.objects.get(pk=self.account.pk).password
        self.assertNotEqual(password, new_password)


class ApiTest(TestCase):

    def setUp(self):
        self.apikey = models.ApiKey.objects.create().key
        self.dk = models.Country.objects.get(name="Denmark")
        self.fgas = models.Obligation.objects.get(code='fgas')

    def test_response_empty_when_no_companies_in_db(self):
        resp = self.client.get('/company/all?apikey=' + self.apikey)
        self.assertEqual(resp['Content-Type'], 'application/xml')
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<companies></companies>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_single_company_from_db(self):
        account = models.Account.objects.create(uid='fgas12345')
        kwargs = dict(ORG_FIXTURE, country=self.dk,
                      account=account, obligation=self.fgas)
        org = models.Company.objects.create(**kwargs)
        models.Person.objects.create(company=org,
                                     first_name="Joe",
                                     family_name="Smith",
                                     email="joe.smith@example.com",
                                     phone="555 1234",
                                     fax="555 6789")

        comment_text = "A comment"
        comment = models.Comment.objects.create(company=org,
                                                text=comment_text)

        resp = self.client.get('/company/all?apikey=' + self.apikey)

        # By default, MySQL DateTime doesn't store fractional seconds,
        # so we'll get them back trimmed
        expected_comment_created = str(comment.created.replace(microsecond=0))

        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<companies>'
                      '<company>'
                        '<pk>' + str(org.pk) + '</pk>'
                        '<name>Teh company</name>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<eori></eori>'
                        '<vat_number></vat_number>'
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
                        '<comment>'
                          '<text>A comment</text>'
                          '<created>' + expected_comment_created + '</created>'
                        '</comment>'
                      '</company>'
                    '</companies>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_all_person_data(self):
        account = models.Account.objects.create(uid='fgas12345')
        kwargs = dict(ORG_FIXTURE, country=self.dk,
                      account=account, obligation=self.fgas)
        org = models.Company.objects.create(**kwargs)
        models.Person.objects.create(company=org,
                                     first_name="Joe",
                                     family_name="Smith",
                                     email="joe.smith@example.com",
                                     phone="555 1234",
                                     phone2="556 1234",
                                     phone3="557 1234",
                                     fax="555 6789")

        resp = self.client.get('/company/all?apikey=' + self.apikey)
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<companies>'
                      '<company>'
                        '<pk>' + str(org.pk) + '</pk>'
                        '<name>Teh company</name>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<eori></eori>'
                        '<vat_number></vat_number>'
                        '<addr_place1>Copenhagen</addr_place1>'
                        '<addr_place2>Hovedstaden</addr_place2>'
                        '<account>fgas12345</account>'
                        '<obligation name="F-gases">fgas</obligation>'
                        '<country name="Denmark">dk</country>'
                        '<person>'
                          '<name>Joe Smith</name>'
                          '<email>joe.smith@example.com</email>'
                          '<phone>555 1234</phone>'
                          '<phone>556 1234</phone>'
                          '<phone>557 1234</phone>'
                          '<fax>555 6789</fax>'
                        '</person>'
                      '</company>'
                    '</companies>')
        self.assertEqual(resp.content, expected)

    def test_response_contains_company_with_matching_uid(self):
        kwargs = dict(ORG_FIXTURE, country=self.dk, obligation=self.fgas)
        account1 = models.Account.objects.create(uid='fgas0001')
        account2 = models.Account.objects.create(uid='fgas0002')
        models.Company.objects.create(account=account1, **kwargs)
        org2 = models.Company.objects.create(account=account2, **kwargs)

        resp = self.client.get('/company/all'
                               '?account_uid=fgas0002'
                               '&apikey=' + self.apikey)
        expected = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<companies>'
                      '<company>'
                        '<pk>' + str(org2.pk) + '</pk>'
                        '<name>Teh company</name>'
                        '<addr_street>teh street</addr_street>'
                        '<addr_postalcode>123456</addr_postalcode>'
                        '<eori></eori>'
                        '<vat_number></vat_number>'
                        '<addr_place1>Copenhagen</addr_place1>'
                        '<addr_place2>Hovedstaden</addr_place2>'
                        '<account>fgas0002</account>'
                        '<obligation name="F-gases">fgas</obligation>'
                        '<country name="Denmark">dk</country>'
                      '</company>'
                    '</companies>')
        self.assertEqual(resp.content, expected)

    def test_requests_with_no_api_key_are_rejected(self):
        resp = self.client.get('/company/all')
        self.assertEqual(resp.status_code, 403)
