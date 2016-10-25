from mock import Mock, patch

from django.core import mail
from django.test.utils import override_settings

from bdr_management.tests import base, factories
from bdr_registry.models import Company, Account


LdapEditorResetPassMock = Mock()
LdapEditorResetPassMock.create_account.return_value = False
LdapEditorResetPassMock.reset_password.return_value = True


LdapEditorCreateAccountMock = Mock()
LdapEditorCreateAccountMock.create_account.return_value = True
LdapEditorCreateAccountMock.reset_password.return_value = False


BDR_API_URL = 'http://testserver'
BDR_API_AUTH = ('apiuser', 'apipassword')


class CompanyResetPasswordTests(base.BaseWebTest):

    def setUp(self):
        self.patcher = patch('bdr_management.backend.create_ldap_editor',
                             Mock(return_value=LdapEditorResetPassMock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_reset_password_get_with_account(self):
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(200, resp.status_int)
        self.assertTemplateUsed(resp, 'bdr_management/reset_password.html')
        self.assertEqual(resp.context['object'], org)

    def test_reset_password_get_without_account(self):
        user = factories.StaffUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_reset_password_post_without_account(self):
        user = factories.StaffUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.post(url, user=user.username, expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_reset_password(self):
        factories.SiteConfigurationFactory()
        org = factories.CompanyWithAccountFactory()
        self.assertIsNone(org.account.password)
        url = self.reverse('management:reset_password', pk=org.pk)
        success_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.post(url, user='admin')
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        org = self.assertObjectInDatabase('Company', app='bdr_registry',
                                          pk=org.pk)
        self.assertIsNotNone(org.account.password)
        expected_messages = [
            "Password has been reset."]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(0, len(mail.outbox))

    def test_reset_password_changes_old(self):
        user = factories.SuperUserFactory()
        account = factories.AccountFactory(password='changeme')
        org = factories.CompanyFactory(account=account)
        url = self.reverse('management:reset_password', pk=org.pk)
        self.app.post(url, user=user.username)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.first(), account)
        self.assertNotEqual(Account.objects.first().password, account.password)

    @override_settings(BDR_EMAIL_FROM='test@eaudeweb.ro')
    def test_reset_password_with_perform_send(self):
        factories.SiteConfigurationFactory()
        obligation = factories.ObligationFactory()
        org = factories.CompanyWithAccountFactory(obligation=obligation)
        self.assertEqual(1, org.people.count())
        email = org.people.first().email
        url = self.reverse('management:reset_password', pk=org.pk)
        success_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.post(url, {'perform_send': '1'}, user='admin')
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        expected_messages = [
            "Password has been reset.",
            'Emails have been sent to 1 person(s).']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

    def test_reset_password_link_with_account(self):
        factories.SiteConfigurationFactory()
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(1, len(resp.pyquery('#reset-password-action')))

    def test_reset_password_link_without_account(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(0, len(resp.pyquery('#reset-password-action')))


class CompanyCreateAccountTests(base.BaseWebTest):

    def setUp(self):
        self.patcher = patch('bdr_management.backend.create_ldap_editor',
                             Mock(return_value=LdapEditorCreateAccountMock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_create_company_account_get_with_account(self):
        factories.SiteConfigurationFactory()
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user='admin', expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_create_company_account_get_without_account(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        self.assertTemplateUsed(resp, 'bdr_management/create_account.html')
        self.assertEqual(resp.context['object'], org)

    def test_create_company_account(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        org = factories.CompanyFactory(obligation=obligation)
        url = self.reverse('management:create_account', pk=org.pk)
        success_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.post(url, user=user.username)
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        org = self.assertObjectInDatabase('Company', app='bdr_registry',
                                          pk=org.pk)
        self.assertIsNotNone(org.account)
        self.assertIsNotNone(org.account.password)

        expected_messages = ["Account created."]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(0, len(mail.outbox))

    @override_settings(BDR_EMAIL_FROM='test@eaudeweb.ro')
    def test_create_company_account_with_perform_send(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        person = factories.PersonFactory()
        org = factories.CompanyFactory(obligation=obligation,
                                       people=[person])
        self.assertEqual(1, org.people.count())
        email = org.people.first().email
        url = self.reverse('management:create_account', pk=org.pk)
        success_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.post(url, {'perform_send': '1'}, user=user.username)
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        expected_messages = ["Account created.",
                             'Emails have been sent to 1 person(s).']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

    def test_create_account_link_with_account(self):
        factories.SiteConfigurationFactory()
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(0, len(resp.pyquery('#create-account-action')))

    def test_create_account_link_without_account(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(1, len(resp.pyquery('#create-account-action')))


class CompanyCreateReportingFolderTests(base.BaseWebTest):

    @override_settings(BDR_API_URL=None, BDR_API_AUTH=None)
    def test_create_reporting_folder_get_without_settings(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:create_reporting_folder', pk=org.pk)
        redirect_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, redirect_url)
        resp = resp.follow()
        expected_messages = ['BDR_API_URL and BDR_API_AUTH not configured']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)

    @override_settings(BDR_API_URL=None, BDR_API_AUTH=None)
    def test_create_reporting_folder_post_without_settings(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:create_reporting_folder', pk=org.pk)
        redirect_url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.post(url, user=user.username)
        self.assertRedirects(resp, redirect_url)
        resp = resp.follow()
        expected_messages = ['BDR_API_URL and BDR_API_AUTH not configured']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)

    @override_settings(BDR_API_URL=BDR_API_URL, BDR_API_AUTH=BDR_API_AUTH)
    def test_create_reporting_folder_get(self):
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:create_reporting_folder', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        self.assertTemplateUsed(
            resp, 'bdr_management/create_reporting_folder.html')


class CompanyNameHistoryTests(base.BaseWebTest):

    def setUp(self):
        self.company_form = {
            'name': "Teh company",
            'addr_street': "teh street",
            'addr_place1': "Copenhagen",
            'addr_postalcode': "123456",
            'addr_place2': "Hovedstaden",
            'country': '1',
            'obligation': '1',
            'vat_number': 'vat number'
        }
        self.person_form = {
            'title': "Mr.",
            'first_name': "Joe",
            'family_name': "Tester",
            'email': "tester@example.com",
            'phone': "555 1234",
        }

        self.user = factories.SuperUserFactory()

    def create_company(self):
        url = self.reverse('management:companies_add')
        self.app.post(
            url,
            self.company_form.items() + self.person_form.items(),
            user='admin')
        company = Company.objects.all().first()
        return company

    def test_create_company_adds_name_history(self):
        factories.SiteConfigurationFactory()
        obligation = factories.ObligationFactory()
        country = factories.CountryFactory()
        self.company_form['obligation'] = obligation.id
        self.company_form['country'] = country.id
        company = self.create_company()
        self.assertEqual(company.namehistory.count(), 1)
        self.assertEqual(company.namehistory.first().name,
                         self.company_form['name'])

    def test_rename_company_adds_name_history(self):
        factories.SiteConfigurationFactory()
        obligation = factories.ObligationFactory()
        country = factories.CountryFactory()
        self.company_form['obligation'] = obligation.id
        self.company_form['country'] = country.id
        company = self.create_company()
        url = self.reverse('management:companies_edit', **{'pk': company.pk})
        old_name = self.company_form['name']
        new_name = 'New name'
        self.company_form.update({'name': new_name})
        self.app.post(url, self.company_form, user=self.user)
        self.assertEqual(company.namehistory.count(), 2)
        self.assertEqual(company.namehistory.first().name, old_name)
        self.assertEqual(company.namehistory.all()[1].name, new_name)
