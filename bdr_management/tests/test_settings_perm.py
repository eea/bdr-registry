from .base import BaseWebTest
from bdr_management.tests import factories


class SettingsTests(BaseWebTest):
    def test_settings_view_by_anonymous(self):
        url = self.reverse("management:settings_view")
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_settings_view_by_staff_user(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        url = self.reverse("management:settings_view")
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_settings_view_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        url = self.reverse("management:settings_view")
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_settings_view_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        url = self.reverse("management:settings_view")
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_settings_update_by_staff(self):
        user = factories.StaffUserFactory()
        url = self.reverse("management:settings_edit")
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_settings_update_by_anonymous(self):
        url = self.reverse("management:settings_edit")
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_settings_update_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        url = self.reverse("management:settings_edit")
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_settings_update_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        url = self.reverse("management:settings_edit")
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
