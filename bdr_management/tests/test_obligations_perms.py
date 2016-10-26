
from .base import BaseWebTest
from bdr_management.tests import factories


class ObligationManagementTests(BaseWebTest):

    def test_obligations_list_by_anonymous(self):
        url = self.reverse('management:obligations')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligations_list_by_staff_user(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligations_list_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligations_list_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_anonymous(self):
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username,)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_add_by_staff(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_add_by_anonymous(self):
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_add_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_update_by_staff(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_update_by_anonymous(self):
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_delete_by_staff(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_delete_by_anonymous(self):
        user = factories.UserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:obligations'))

    def test_obligation_delete_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:obligations'))

    def test_obligation_update_by_bdr_group_check_admins(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        obligation.admins = [user]
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

        resp = self.app.post(url, {'name': obligation.name,
            'code': obligation.code,
            'reportek_slug': obligation.reportek_slug,
            'email_template': obligation.email_template.id,
            'bcc': obligation.bcc,
            'admins': [u.id for u in obligation.admins.all()]},
            user=user.username)

        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], url)

        user_obligations = user.obligations.values()
        self.assertEqual(len(user_obligations), 1)
        self.assertEqual(user_obligations[0]['id'], obligation.id)
