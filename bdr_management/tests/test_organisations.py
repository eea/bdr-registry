from mock import Mock, patch

from django.core import mail
from django.test.utils import override_settings

from bdr_management.tests import base, factories


LdapEditorResetPassMock = Mock()
LdapEditorResetPassMock.create_account.return_value = False
LdapEditorResetPassMock.reset_password.return_value = True


LdapEditorCreateAccountMock = Mock()
LdapEditorCreateAccountMock.create_account.return_value = True
LdapEditorCreateAccountMock.reset_password.return_value = False


BDR_API_URL = 'http://testserver'
BDR_API_AUTH = ('apiuser', 'apipassword')


class OrganisationResetPasswordTests(base.BaseWebTest):

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

    # def test_reset_passowrd_get_without_obligation(self):
    #     org = factories.OrganisationWithAccountFactory()
    #     url = self.reverse('management:reset_password', pk=org.pk)
    #     resp = self.app.post(url, user=user.username, expect_errors=True)
    #     self.assertEqual(404, resp.status_int)

    # def test_reset_passowrd_post_without_obligation(self):
    #     org = factories.OrganisationWithAccountFactory()
    #     url = self.reverse('management:reset_password', pk=org.pk)
    #     resp = self.app.post(url, user=user.username, expect_errors=True)
    #     self.assertEqual(404, resp.status_int)

    def test_reset_password(self):
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
            "Password have been reset. LDAP: {'password': 1}."]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(0, len(mail.outbox))

    def test_reset_password_with_perform_send(self):
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
            "Password have been reset. LDAP: {'password': 1}.",
            'Emails have been sent to 1 people.']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

    def test_reset_password_link_with_account(self):
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(1, len(resp.pyquery('#reset-password-action')))

    def test_reset_password_link_without_account(self):
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(0, len(resp.pyquery('#reset-password-action')))


class OrganisationCreateAccountTests(base.BaseWebTest):

    def setUp(self):
        self.patcher = patch('bdr_management.backend.create_ldap_editor',
                             Mock(return_value=LdapEditorCreateAccountMock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_create_organisation_account_get_with_account(self):
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user='admin', expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_create_organisation_account_get_without_account(self):
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        self.assertTemplateUsed(resp, 'bdr_management/create_account.html')
        self.assertEqual(resp.context['object'], org)

    def test_create_organisation_account(self):
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

        expected_messages = ["Account created. LDAP: {'create': 1}."]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(0, len(mail.outbox))

    def test_create_organisation_account_with_perform_send(self):
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
        expected_messages = ["Account created. LDAP: {'create': 1}.",
                             'Emails have been sent to 1 people.']
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

    def test_create_account_link_with_account(self):
        org = factories.CompanyWithAccountFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(0, len(resp.pyquery('#create-account-action')))

    def test_create_account_link_without_account(self):
        user = factories.SuperUserFactory()
        org = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(1, len(resp.pyquery('#create-account-action')))


class OrganisationCreateReportingFolderTests(base.BaseWebTest):

    def test_create_reporting_folder_get_without_settings(self):
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

    def test_create_reporting_folder_post_without_settings(self):
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
