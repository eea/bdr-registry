
from .base import BaseWebTest
from bdr_management.tests import factories


class PersonManagementTests(BaseWebTest):

    def test_persons_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:persons'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_persons_view_by_anonymous(self):
        url = self.reverse('management:persons')
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_view_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_view', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_view_by_anonymous(self):
        person = factories.PersonFactory()
        url = self.reverse('management:persons_view', pk=person.pk)
        resp = self.app.get(url, user=None)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_by_anonymous(self):
        user = factories.UserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_by_superuser(self):
        user = factories.SuperUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_delete_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_anonymous(self):
        user = factories.UserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, '/management/persons')


class PersonTests(BaseWebTest):

    def test_person_view_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_view_by_anonymous(self):
        person = factories.PersonFactory()
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=None)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_view_by_superuser(self):
        user = factories.SuperUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory(id=100)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_anonymous(self):
        company = factories.CompanyFactory(id=100)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory(id=100)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_by_owner(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_by_superuser(self):
        user = factories.SuperUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_delete_by_staff_user(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_person_delete_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)

        self.assertRedirects(resp, success_url)

    def test_person_delete_by_anonymous(self):
        company = factories.CompanyFactory()
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person.pk)
        resp = self.app.delete(url)
        self.assertRedirects(resp, self.get_login_for_url(url))
