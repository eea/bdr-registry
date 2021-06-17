import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from django.core import mail
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import Client, override_settings, TransactionTestCase
from django.urls import reverse

from bdr_registry import models
from bdr_management.tests import factories, base

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ORG_FIXTURE = {
    "name": "Teh company",
    "addr_street": "teh street",
    "addr_place1": "Copenhagen",
    "addr_postalcode": "123456",
    "addr_place2": "Hovedstaden",
    "vat_number": "vat number",
}

ORG_FIXTURE_HDV = {
    "name": "Teh company",
    "addr_street": "teh street",
    "addr_place1": "Copenhagen",
    "addr_postalcode": "123456",
    "world_manufacturer_identifier": "test1234",
}

PERSON_FIXTURE = {
    "title": "Mr.",
    "first_name": "Joe",
    "family_name": "Tester",
    "email": "tester@example.com",
    "phone": "555 1234",
}

COMMENT_FIXTURE = {"text": "This is a comment"}


class FormSubmitTest(TransactionTestCase):
    def setUp(self):
        self.denmark = factories.CountryFactory(name="Denmark", code="dk")
        self.obligation = factories.ObligationFactory(code="obl", name="Obligation")
        factories.ObligationFactory(code="hdv", name="HDV")

    def assert_object_has_items(self, obj, data):
        for key in data:
            self.assertEqual(getattr(obj, key), data[key])

    def prepare_form_data(self, org_fixture):
        form_data = {
            "company-country": self.denmark.pk,
            "company-obligation": self.obligation.pk,
            "company-captcha_0": "PASSED",
            "company-captcha_1": "PASSED",
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE(),
        }
        for key, value in org_fixture.items():
            form_data["company-" + key] = value
        for key, value in PERSON_FIXTURE.items():
            form_data["person-" + key] = value
        for key, value in COMMENT_FIXTURE.items():
            form_data["comment-" + key] = value
        return form_data

    def test_submitted_company_and_person_are_saved(self):
        factories.SiteConfigurationFactory()

        resp = self.client.post(
            reverse("self_register"), self.prepare_form_data(ORG_FIXTURE)
        )

        self.assertEqual(models.Company.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        org = models.Company.objects.all()[0]
        person = models.Person.objects.all()[0]

        self.assert_object_has_items(org, ORG_FIXTURE)
        self.assert_object_has_items(person, PERSON_FIXTURE)
        self.assertEqual(person.company, org)
        self.assertCountEqual(org.people.all(), [person])

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["location"], "/self_register/done/")

    def test_submitted_company_and_person_are_saved_on_hdv(self):
        factories.SiteConfigurationFactory()
        data = self.prepare_form_data(ORG_FIXTURE_HDV)
        resp = self.client.post(reverse("self_register_hdv"), data)
        self.assertEqual(models.Company.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        org = models.Company.objects.all()[0]
        person = models.Person.objects.all()[0]

        self.assert_object_has_items(org, ORG_FIXTURE_HDV)
        self.assert_object_has_items(person, PERSON_FIXTURE)
        self.assertEqual(person.company, org)
        self.assertCountEqual(org.people.all(), [person])

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["location"], "/self_register/done/hdv/")

    def test_invalid_person_rolls_back_saved_company(self):
        form_data = self.prepare_form_data(ORG_FIXTURE)
        del form_data["person-email"]
        resp = self.client.post(reverse("self_register"), form_data)

        self.assertEqual(models.Company.objects.count(), 0)
        self.assertEqual(resp.status_code, 200)

    @override_settings(CAPTCHA_TEST_MODE=True)
    def test_mail_is_sent_after_successful_self_registration(self):
        factories.SiteConfigurationFactory()

        user1 = User.objects.create(
            username="user1",
            password="pass1",
            email="example@example.com",
            is_staff=True,
        )
        user2 = User.objects.create(
            username="user2",
            password="pass2",
            email="example@example.com",
            is_staff=True,
        )

        bdr_group = Group.objects.get_or_create(name=settings.BDR_HELPDESK_GROUP)[0]
        bdr_group.user_set.add(user1)
        bdr_group.user_set.add(user2)

        self.obligation.admins.set([user1])

        self.client.post(reverse("self_register"), self.prepare_form_data(ORG_FIXTURE))
        self.assertEqual(len(mail.outbox), 1)


class ApiTest(base.BaseWebTest):
    def setUp(self):
        self.apikey = models.ApiKey.objects.create().key
        self.dk = factories.CountryFactory(name="Denmark", code="dk")
        self.obligation = factories.ObligationFactory(code="obl", name="Obligation")

    def test_response_empty_when_no_companies_in_db(self):
        resp = self.client.get("/organisation/all?apikey=" + self.apikey, follow=True)
        self.assertEqual(resp["Content-Type"], "application/xml")
        expected = (
            '<?xml version="1.0" encoding="utf-8"?>\n' "<organisations></organisations>"
        )
        self.assertEqual(resp.content.decode(), expected)

    def test_response_contains_single_company_from_db(self):
        account = models.Account.objects.create(uid="ods12345")
        kwargs = dict(
            ORG_FIXTURE, country=self.dk, account=account, obligation=self.obligation
        )
        org = models.Company.objects.create(**kwargs)
        models.Person.objects.create(
            company=org,
            first_name="Joe",
            family_name="Smith",
            email="joe.smith@example.com",
            phone="555 1234",
            fax="555 6789",
        )

        comment_text = "A comment"
        comment = models.Comment.objects.create(company=org, text=comment_text)

        resp = self.client.get("/organisation/all?apikey=" + self.apikey, follow=True)

        # By default, MySQL DateTime doesn't store fractional seconds,
        # so we'll get them back trimmed
        expected_comment_created = str(comment.created)

        expected = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<organisations>"
            "<organisation>"
            "<pk>" + str(org.pk) + "</pk>"
            "<name>Teh company</name>"
            "<addr_street>teh street</addr_street>"
            "<addr_postalcode>123456</addr_postalcode>"
            "<eori></eori>"
            "<vat_number>vat number</vat_number>"
            "<addr_place1>Copenhagen</addr_place1>"
            "<addr_place2>Hovedstaden</addr_place2>"
            "<active>true</active>"
            "<account>ods12345</account>"
            '<obligation name="Obligation">obl</obligation>'
            '<country name="Denmark">dk</country>'
            "<person>"
            "<name>Joe Smith</name>"
            "<email>joe.smith@example.com</email>"
            "<phone>555 1234</phone>"
            "<fax>555 6789</fax>"
            "</person>"
            "<comment>"
            "<text>A comment</text>"
            "<created>" + expected_comment_created + "</created>"
            "</comment>"
            "</organisation>"
            "</organisations>"
        )
        self.assertEqual(resp.content.decode(), expected)

    def test_response_contains_all_person_data(self):
        account = models.Account.objects.create(uid="ods12345")
        kwargs = dict(
            ORG_FIXTURE, country=self.dk, account=account, obligation=self.obligation
        )
        org = models.Company.objects.create(**kwargs)
        models.Person.objects.create(
            company=org,
            first_name="Joe",
            family_name="Smith",
            email="joe.smith@example.com",
            phone="555 1234",
            phone2="556 1234",
            phone3="557 1234",
            fax="555 6789",
        )
        resp = self.client.get("/organisation/all?apikey=" + self.apikey, follow=True)
        expected = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<organisations>"
            "<organisation>"
            "<pk>" + str(org.pk) + "</pk>"
            "<name>Teh company</name>"
            "<addr_street>teh street</addr_street>"
            "<addr_postalcode>123456</addr_postalcode>"
            "<eori></eori>"
            "<vat_number>vat number</vat_number>"
            "<addr_place1>Copenhagen</addr_place1>"
            "<addr_place2>Hovedstaden</addr_place2>"
            "<active>true</active>"
            "<account>ods12345</account>"
            '<obligation name="Obligation">obl</obligation>'
            '<country name="Denmark">dk</country>'
            "<person>"
            "<name>Joe Smith</name>"
            "<email>joe.smith@example.com</email>"
            "<phone>555 1234</phone>"
            "<phone>556 1234</phone>"
            "<phone>557 1234</phone>"
            "<fax>555 6789</fax>"
            "</person>"
            "</organisation>"
            "</organisations>"
        )
        self.assertEqual(resp.content.decode(), expected)

    def test_response_contains_company_with_matching_uid(self):
        kwargs = dict(ORG_FIXTURE, country=self.dk, obligation=self.obligation)
        account1 = models.Account.objects.create(uid="ods0001")
        account2 = models.Account.objects.create(uid="ods0002")
        models.Company.objects.create(account=account1, **kwargs)
        org2 = models.Company.objects.create(account=account2, **kwargs)

        resp = self.client.get(
            "/organisation/all" "?account_uid=ods0002" "&apikey=" + self.apikey,
            follow=True,
        )
        expected = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<organisations>"
            "<organisation>"
            "<pk>" + str(org2.pk) + "</pk>"
            "<name>Teh company</name>"
            "<addr_street>teh street</addr_street>"
            "<addr_postalcode>123456</addr_postalcode>"
            "<eori></eori>"
            "<vat_number>vat number</vat_number>"
            "<addr_place1>Copenhagen</addr_place1>"
            "<addr_place2>Hovedstaden</addr_place2>"
            "<active>true</active>"
            "<account>ods0002</account>"
            '<obligation name="Obligation">obl</obligation>'
            '<country name="Denmark">dk</country>'
            "</organisation>"
            "</organisations>"
        )
        self.assertEqual(resp.content.decode(), expected)

    # todo rewrite after auth api authorization is removed
    # def test_requests_with_no_api_key_are_rejected(self):
    #     factories.CountryFactory()
    #     resp = self.client.get('/organisation/all')f
    #     self.assertEqual(resp.status_code, 403)

    def test_api_company_by_obligation(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory(code="obl", name="Obligation")
        company = factories.CompanyFactory(obligation=obligation)
        url = self.reverse(
            "api_company_by_obligation", obligation_slug=obligation.reportek_slug
        )
        user.set_password("q")
        user.save()
        Client(HTTP_USER_AGENT="Mozilla/5.0")
        self.client.login(username=user.username, password="q")
        resp = self.client.get(url)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], company.name)
