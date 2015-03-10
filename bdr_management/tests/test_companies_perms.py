from .base import BaseWebTest
from bdr_management.tests import factories
from bdr_registry.models import Company, Person


class CompanyManagementTests(BaseWebTest):
    def test_company_add_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_add_post_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        url = self.reverse('management:companies_add')
        form = factories.company_with_person_form()
        resp = self.app.post(url, params=form, user=user, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertFalse(Company.objects.exists())
        self.assertFalse(Person.objects.exists())

    def test_company_add_by_anonymous(self):
        factories.SiteConfigurationFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_add_post_by_anonymous(self):
        factories.SiteConfigurationFactory()
        url = self.reverse('management:companies_add')
        form = factories.company_with_person_form()
        resp = self.app.post(url, params=form, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertFalse(Company.objects.exists())
        self.assertFalse(Person.objects.exists())

    def test_company_add_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_add_post_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        country = factories.CountryFactory()
        url = self.reverse('management:companies_add')
        form = factories.company_with_person_form()
        form['country'] = country.id
        form['obligation'] = obligation.id
        resp = self.app.post(url, params=form, user=user)
        self.assertRedirects(resp, self.reverse('management:companies'))
        self.assertTrue(Company.objects.exists())
        self.assertTrue(Person.objects.exists())

    def test_company_add_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        url = self.reverse('management:companies_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_add_post_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        country = factories.CountryFactory()
        url = self.reverse('management:companies_add')
        form = factories.company_with_person_form()
        form['country'] = country.id
        form['obligation'] = obligation.id
        resp = self.app.post(url, params=form, user=user)
        self.assertRedirects(resp, self.reverse('management:companies'))
        self.assertTrue(Company.objects.exists())
        self.assertTrue(Person.objects.exists())

    def test_companies_view_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:companies'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_companies_view_by_anonymous(self):
        factories.SiteConfigurationFactory()
        url = self.reverse('management:companies')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_view_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_view_by_anonymous(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_view', pk=company.pk)
        resp = self.app.get(url, user=None, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_update_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_update_by_anonymous(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_update_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_update_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_staff_cant_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'name': 'NewName'})
        resp = self.app.post(url, user=user.username, params=form,
                             expect_errors=True)

        self.assertEqual(resp.status_int, 403)
        self.assertObjectInDatabase(Company, name=company.name)
        self.assertObjectNotInDatabase(Company, name='NewName')

    def test_anonymous_cant_edit_company(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'name': 'NewName'})
        resp = self.app.post(url, params=form, expect_errors=True)

        self.assertEqual(resp.status_int, 403)
        self.assertObjectInDatabase(Company, name=company.name)
        self.assertObjectNotInDatabase(Company, name='NewName')

    def test_bdr_group_can_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'name': 'NewName'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(
            resp,
            self.reverse('management:companies_view', pk=company.pk))
        self.assertObjectInDatabase(Company, name='NewName')
        self.assertObjectNotInDatabase(Company, name=company.name)

    def test_superuser_can_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_edit', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'name': 'NewName'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(
            resp,
            self.reverse('management:companies_view', pk=company.pk))
        self.assertObjectInDatabase(Company, name='NewName')
        self.assertObjectNotInDatabase(Company, name=company.name)

    def test_company_delete_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_delete_by_anonymous(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_delete_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:companies_delete',
                           pk=company.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:companies'))


class CompanyTests(BaseWebTest):
    def test_company_view_by_owner(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_view_by_anonymous(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_company_view_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_view_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_update_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(403, resp.status_int)

    def test_company_update_by_owner(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_update_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_company_update_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_staff_cant_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'website': 'http://www.google.com/'})
        resp = self.app.post(url, user=user.username, params=form,
                             expect_errors=True)

        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Company, website=form['website'])
        self.assertObjectInDatabase(Company, website=None)

    def test_anonymous_cant_edit_company(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'website': 'http://www.google.com/'})
        resp = self.app.post(url, params=form, expect_errors=True)

        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Company, website=form['website'])
        self.assertObjectInDatabase(Company, website=None)

    def test_bdr_group_can_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'website': 'http://www.google.com/'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(
            resp,
            self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Company, website=form['website'])
        self.assertObjectNotInDatabase(Company, website=None)

    def test_superuser_can_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'website': 'http://www.google.com/'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(
            resp,
            self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Company, website=form['website'])
        self.assertObjectNotInDatabase(Company, website=None)

    def test_owner_cant_change_company_name(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'name': 'NewName'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(resp, self.reverse('company', pk=company.pk))
        self.assertObjectNotInDatabase(Company, name='NewName')
        self.assertObjectInDatabase(Company, name=company.name)

    def test_owner_can_edit_company(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('company_update', pk=company.pk)
        form = self.get_company_form_params(company)
        form.update({'website': 'http://www.google.com/'})
        resp = self.app.post(url, user=user.username, params=form)

        self.assertRedirects(resp, self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Company, website=form['website'])
        self.assertObjectNotInDatabase(Company, website=None)
