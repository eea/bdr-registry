
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationManagementTests(BaseWebTest):

    def test_organisation_add_by_staff(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_add_by_anonymous(self):
        url = self.reverse('management:companies_add')
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_add_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_companies_view_by_staff(self):
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:companies'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_companies_view_by_anonymous(self):
        url = self.reverse('management:companies')
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_view_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=company.pk)
        resp = self.app.get(url, user=None)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_anonymous(self):
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_delete_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_delete_by_anonymous(self):
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:companies'))


class OrganisationTests(BaseWebTest):

    def test_organisation_view_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_anonymous(self):
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_organisation_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        resp.follow()

    def test_organisation_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
