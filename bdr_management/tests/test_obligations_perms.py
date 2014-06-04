
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
