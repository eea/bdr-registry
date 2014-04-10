
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationManagementTests(BaseWebTest):

    def test_organisations_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:organisations'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisations_view_by_anonymous(self):
        url = self.reverse('management:organisations')
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_view_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_anonymous(self):
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view', pk=organisation.pk)
        resp = self.app.get(url, user=None)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_edit', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_anonymous(self):
        user = factories.UserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_edit', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_edit', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_edit', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_delete_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_delete',
                           pk=organisation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_delete_by_anonymous(self):
        user = factories.UserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_delete',
                           pk=organisation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_delete',
                           pk=organisation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, '/management/organisations')


class OrganisationTests(BaseWebTest):

    def test_organisation_view_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(account=account)
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_anonymous(self):
        user = factories.UserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation_update', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        resp.follow()

    def test_organisation_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(account=account)
        url = self.reverse('organisation_update', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation_update', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation_update', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
