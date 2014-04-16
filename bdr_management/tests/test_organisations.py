from django.core import mail
from mock import Mock, patch

from bdr_management.tests import base, factories


LdapEditorResetPassMock = Mock()
LdapEditorResetPassMock.create_account.return_value = False
LdapEditorResetPassMock.reset_password.return_value = True


LdapEditorCreateAccountMock = Mock()
LdapEditorCreateAccountMock.create_account.return_value = True
LdapEditorCreateAccountMock.reset_password.return_value = False


class OrganisationResetPasswordTests(base.BaseWebTest):

    def setUp(self):
        self.patcher = patch('bdr_management.backend.create_ldap_editor',
                             Mock(return_value=LdapEditorResetPassMock))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_reset_password_get_with_account(self):
        org = factories.OrganisationWithAccountFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(200, resp.status_int)
        self.assertEqual('Reset password for %s' % org.name,
                         resp.pyquery.find('h1').text())

    def test_reset_passowrd_get_without_account(self):
        user = factories.StaffUserFactory()
        org = factories.OrganisationFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_reset_passowrd_post_without_account(self):
        user = factories.StaffUserFactory()
        org = factories.OrganisationFactory()
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
        org = factories.OrganisationWithAccountFactory()
        self.assertFalse(org.account.password)
        url = self.reverse('management:reset_password', pk=org.pk)
        success_url = self.reverse('management:organisations_view', pk=org.pk)
        resp = self.app.post(url, user='admin')
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        org = self.assertObjectInDatabase('Organisation', app='bdr_registry',
                                          pk=org.pk)
        self.assertTrue(org.account.password)
        msg = [str(m) for m in resp.context['messages']]
        self.assertTrue(msg)
        self.assertEqual("Password have been reset. LDAP: {'password': 1}.",
                         msg[0])
        self.assertEqual(0, len(mail.outbox))

    def test_reset_password_with_perform_send(self):
        obligation = factories.ObligationFactory()
        org = factories.OrganisationWithAccountFactory(obligation=obligation)
        self.assertEqual(1, org.people.count())
        email = org.people.all()[0].email
        url = self.reverse('management:reset_password', pk=org.pk)
        success_url = self.reverse('management:organisations_view', pk=org.pk)
        resp = self.app.post(url, {'perform_send': '1'}, user='admin')
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        msg = [str(m) for m in resp.context['messages']]
        self.assertTrue(msg)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

    def test_reset_password_link_with_account(self):
        org = factories.OrganisationWithAccountFactory()
        url = self.reverse('management:organisations_view', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(1, len(resp.pyquery('#reset-password-action')))

    def test_reset_password_link_without_account(self):
        user = factories.SuperUserFactory()
        org = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view', pk=org.pk)
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
        org = factories.OrganisationWithAccountFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user='admin', expect_errors=True)
        self.assertEqual(404, resp.status_int)


    def test_create_organisation_account_get_without_account(self):
        user = factories.BDRGroupUserFactory()
        org = factories.OrganisationFactory()
        url = self.reverse('management:create_account', pk=org.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        self.assertEqual('Create account for %s' % org.name,
                         resp.pyquery.find('h1').text())

    def test_create_organisation_account(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        org = factories.OrganisationFactory(obligation=obligation)
        url = self.reverse('management:create_account', pk=org.pk)
        success_url = self.reverse('management:organisations_view', pk=org.pk)
        resp = self.app.post(url, user=user.username)
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        org = self.assertObjectInDatabase('Organisation', app='bdr_registry',
                                          pk=org.pk)
        self.assertTrue(org.account)
        self.assertTrue(org.account.password)

        msg = [str(m) for m in resp.context['messages']]
        self.assertTrue(msg)
        self.assertEqual("Account created. LDAP: {'create': 1}.",
                         msg[0])
        self.assertEqual(0, len(mail.outbox))

    def test_create_organisation_account_with_perform_send(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        person = factories.PersonFactory()
        org = factories.OrganisationFactory(obligation=obligation, people=[person])
        self.assertEqual(1, org.people.count())
        email = org.people.all()[0].email
        url = self.reverse('management:create_account', pk=org.pk)
        success_url = self.reverse('management:organisations_view', pk=org.pk)
        resp = self.app.post(url, {'perform_send': '1'}, user=user.username)
        self.assertRedirects(resp, success_url)
        resp = resp.follow()
        msg = [str(m) for m in resp.context['messages']]
        self.assertTrue(msg)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(email, mail.outbox[0].to)

