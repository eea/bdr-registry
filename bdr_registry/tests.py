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

    def test_submitted_company_is_saved(self):
        form_data = dict(ORG_FIXTURE, country=self.denmark.pk)
        resp = self.client.post('/company/add', form_data)

        self.assertEqual(models.Company.objects.count(), 1)
        org = models.Company.objects.all()[0]
        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assertEqual(org.country, self.denmark)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver/company/%d' % org.pk)

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


class OrganisationExportTest(TestCase):

    def setUp(self):
        self.dk = models.Country.objects.get(name="Denmark")
        user = create_user_and_login(self.client, superuser=True, staff=True)
        form_data = dict(ORG_FIXTURE, country=self.dk.pk)
        resp = self.client.post('/company/add', form_data)
        self.assertEqual(resp.status_code, 302)


    def test_export_csv_no_obligation(self):
        resp = self.client.get('/admin/bdr_registry/company/export')
        self.assertIn(ORG_FIXTURE['name'], resp.content)

    def test_export_csv_with_obligation(self):
        fgas = models.Obligation.objects.get(code='fgas')
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, obligation=fgas.pk)
        org_pk = models.Company.objects.all()[0].pk

        # we need to refer the form that is tested.
        # see https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation
        org_form.update({
            'people-INITIAL_FORMS': '0',
            'people-TOTAL_FORMS': '0',
            'comments-INITIAL_FORMS': '0',
            'comments-TOTAL_FORMS': '0'
        })

        resp = self.client.post(
            '/admin/bdr_registry/company/{0}/'.format(org_pk),
            org_form)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/admin/bdr_registry/company/export')
        self.assertIn(OBLIGATON_CODE, resp.content)


class OrganisationEditTest(TestCase):

    def setUp(self):
        self.dk = models.Country.objects.get(name="Denmark")
        org_data = dict(ORG_FIXTURE, country=self.dk.pk)
        self.client.post('/company/add', org_data)
        self.org = models.Company.objects.all()[0]
        self.update_url = '/company/%d/update' % self.org.pk

    def test_model_updated_from_company_edit(self):
        create_user_and_login(self.client, superuser=True)
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, addr_street="Sesame")
        self.client.post(self.update_url, org_form)
        new_org = models.Company.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.addr_street, "Sesame")

    def test_modifying_obligation_or_account_is_ignored(self):
        create_user_and_login(self.client, superuser=True)
        fgas = models.Obligation.objects.get(code='fgas')
        account = models.Account.objects.create(uid='fgas12345')
        org_form = dict(ORG_FIXTURE, country=self.dk.pk,
                        obligation=fgas.pk, account=account.pk)
        self.client.post(self.update_url, org_form)
        new_org = models.Company.objects.get(pk=self.org.pk)
        self.assertIsNone(new_org.obligation)
        self.assertIsNone(new_org.account)

    def test_company_account_is_allowed_to_edit(self):
        user = create_user_and_login(self.client)
        self.org.account = models.Account.objects.create(uid=user.username)
        self.org.save()
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, addr_street="Sesame")
        resp = self.client.post(self.update_url, org_form)
        self.assertFalse(resp['location'].startswith(LOGIN_PREFIX))
        new_org = models.Company.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.addr_street, "Sesame")

    def test_random_account_is_not_allowed_to_edit(self):
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, addr_street="Sesame")
        resp = self.client.post(self.update_url, org_form)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['location'].startswith(LOGIN_PREFIX))

    def test_view_returns_404_for_company_notfound(self):
        with quiet_request_logging():
            resp = self.client.get('/company/123/update')
        self.assertEqual(resp.status_code, 404)

    def test_admin_can_change_name(self):
        user = create_user_and_login(self.client, superuser=True, staff=True)
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, name="Rebranded")
        resp = self.client.post(self.update_url, org_form)
        self.assertFalse(resp['location'].startswith(LOGIN_PREFIX))
        new_org = models.Company.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.name, "Rebranded")

    def test_owner_cant_change_name(self):
        user = create_user_and_login(self.client)
        self.org.account = models.Account.objects.create(uid=user.username)
        self.org.save()
        org_form = dict(ORG_FIXTURE, country=self.dk.pk, name="Rebranded")
        resp = self.client.post(self.update_url, org_form)
        self.assertFalse(resp['location'].startswith(LOGIN_PREFIX))
        new_org = models.Company.objects.get(pk=self.org.pk)
        self.assertEqual(new_org.name, "Teh company")

    def test_landing_page_redirects_to_company_edit(self):
        self.org.account = models.Account.objects.create(uid='ods123')
        self.org.save()
        url1 = ('http://testserver/edit_company?uid={org.account.uid}'
                .format(org=self.org))
        url2 = ('http://testserver/company/{org.pk}/update'
                .format(org=self.org))
        resp = self.client.get(url1)
        self.assertEqual(resp['location'], url2)


class OrganisationNameHistoryTest(TestCase):

    def setUp(self):
        self.fgas = models.Obligation.objects.get(code='fgas')
        self.dk = models.Country.objects.get(name="Denmark")

    def test_new_company_creates_record_in_history(self):
        user = create_user_and_login(self.client)
        form_data = dict(ORG_FIXTURE, country=self.dk.pk)
        self.client.post('/company/add', form_data)
        self.assertEqual(models.CompanyNameHistory.objects.count(), 1)
        [hist0] = models.CompanyNameHistory.objects.all()
        self.assertEqual(hist0.name, ORG_FIXTURE['name'])
        self.assertEqual(hist0.company, models.Company.objects.get())
        self.assertEqual(hist0.user, user)

    def test_updating_company_name_creates_record_in_history(self):
        form_data = dict(ORG_FIXTURE, country=self.dk.pk)
        self.client.post('/company/add', form_data)
        org = models.Company.objects.all()[0]

        user = create_user_and_login(self.client, superuser=True, staff=True)
        update_url = '/company/%d/update' % org.pk
        form_data['name'] = "Teh other company"
        self.client.post(update_url, form_data)
        self.assertEqual(models.CompanyNameHistory.objects.count(), 2)
        [hist0, hist1] = models.CompanyNameHistory.objects.all()
        self.assertEqual(hist1.name, form_data['name'])
        self.assertEqual(hist1.company, models.Company.objects.get())
        self.assertEqual(hist1.user, user)


class OrganisationPasswordTest(TestCase):

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

    def test_password_email_is_sent(self):
        self.acme.people.create(email="alice@example.com")
        self.acme.people.create(email="bob@example.com")
        create_user_and_login(self.client, superuser=True, staff=True)
        self.client.post('/admin/bdr_registry/company/', {
            helpers.ACTION_CHECKBOX_NAME: self.acme.pk,
            'action': 'send_password_email',
            'perform_send': 'yes',
        })
        self.assertEqual(len(mail.outbox), 2)
        message = mail.outbox[1]
        self.assertItemsEqual(message.to, ['bob@example.com'])
        self.assertIn(self.acme.country.name, message.body)
        self.assertIn(self.acme.account.uid, message.body)
        self.assertIn(self.acme.account.password, message.body)


class PersonEditTest(TestCase):

    def setUp(self):
        self.dk = models.Country.objects.get(name="Denmark")
        self.fgas = models.Obligation.objects.get(code='fgas')
        self.acme = models.Company.objects.create(country=self.dk,
                                                       obligation=self.fgas)
        self.person = models.Person.objects.create(company=self.acme)
        self.update_url = '/person/%d/update' % self.person.pk

    def test_person_information_is_updated(self):
        create_user_and_login(self.client, superuser=True)
        person_form = dict(PERSON_FIXTURE, phone='555 9876')
        self.client.post(self.update_url, person_form)
        new_person = models.Person.objects.get(pk=self.person.pk)
        self.assertEqual(new_person.phone, '555 9876')

    def test_modifying_company_is_ignored(self):
        create_user_and_login(self.client, superuser=True)
        org2 = models.Company.objects.create(country=self.dk,
                                                  obligation=self.fgas)
        person_form = dict(PERSON_FIXTURE, company=org2.pk)
        self.client.post(self.update_url, person_form)
        new_person = models.Person.objects.get(pk=self.person.pk)
        self.assertEqual(new_person.company, self.acme)

    def test_company_account_is_allowed_to_edit(self):
        user = create_user_and_login(self.client)
        account = models.Account.objects.create(uid=user.username)
        self.acme.account = account
        self.acme.save()
        person_form = dict(PERSON_FIXTURE, phone='555 9876')
        resp = self.client.post(self.update_url, person_form)
        self.assertFalse(resp['location'].startswith(LOGIN_PREFIX))
        new_person = models.Person.objects.get(pk=self.person.pk)
        self.assertEqual(new_person.phone, '555 9876')

    def test_random_account_is_not_allowed_to_edit(self):
        create_user_and_login(self.client)
        person_form = dict(PERSON_FIXTURE, phone='555 9876')
        resp = self.client.post(self.update_url, person_form)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['location'].startswith(LOGIN_PREFIX))

    def test_person_update_returns_404_if_person_missing(self):
        with quiet_request_logging():
            resp = self.client.get('/person/123/update')
        self.assertEqual(resp.status_code, 404)

    def test_add_person_to_company(self):
        user = create_user_and_login(self.client)
        account = models.Account.objects.create(uid=user.username)
        self.acme.account = account
        self.acme.save()
        self.client.post('/company/%d/add_person' % self.acme.pk,
                         dict(PERSON_FIXTURE, first_name='Smith'))
        new_person = models.Person.objects.get(first_name='Smith')
        self.assertEqual(new_person.company, self.acme)

    def test_add_person_to_company_returns_404_for_missing_org(self):
        with quiet_request_logging():
            resp = self.client.get('/company/123/add_person')
        self.assertEqual(resp.status_code, 404)

    def test_company_account_can_delete_person_from_company(self):
        self.person2 = models.Person.objects.create(company=self.acme)
        user = create_user_and_login(self.client)
        account = models.Account.objects.create(uid=user.username)
        self.acme.account = account
        self.acme.save()
        self.client.post('/person/%d/delete' % self.person.pk)
        self.assertItemsEqual(self.acme.people.all(), [self.person2])

    def test_company_account_cant_delete_last_person(self):
        user = create_user_and_login(self.client)
        account = models.Account.objects.create(uid=user.username)
        self.acme.account = account
        self.acme.save()
        self.client.post('/person/%d/delete' % self.person.pk)
        self.assertItemsEqual(self.acme.people.all(), [self.person])

    def test_random_account_is_not_allowed_to_delete(self):
        create_user_and_login(self.client)
        self.client.post('/person/%d/delete' % self.person.pk)
        #self.assertEqual([p.pk for p in self.acme.people.all()],
        #                 [self.person.pk])
        self.assertItemsEqual(self.acme.people.all(), [self.person])

    def test_person_delete_returns_404_if_person_missing(self):
        with quiet_request_logging():
            resp = self.client.get('/person/123/delete')
        self.assertEqual(resp.status_code, 404)


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
