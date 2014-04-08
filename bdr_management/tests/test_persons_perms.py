
from .base import BaseWebTest
from bdr_management.tests import factories


class PersonTests(BaseWebTest):

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

    def test_person_view_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        person = factories.PersonFactory(organisation=organisation)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_view_update_by_anonymous(self):
        person = factories.PersonFactory()
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=None)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_view_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        person = factories.PersonFactory(organisation=organisation)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_view_update_by_superuser(self):
        user = factories.SuperUserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        person = factories.PersonFactory(organisation=organisation)
        url = self.reverse('person', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_management_add_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:persons_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_management_add_by_anonymous(self):
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:persons_add', pk=organisation.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_management_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:persons_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_management_add_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:persons_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory(id=100)
        url = self.reverse('organisation_add_person', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_anonymous(self):
        organisation = factories.OrganisationFactory(id=100)
        url = self.reverse('organisation_add_person', pk=organisation.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory(id=100)
        url = self.reverse('organisation_add_person', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_by_owner(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        url = self.reverse('organisation_add_person', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_edit_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_edit_by_anonymous(self):
        user = factories.UserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_edit_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        person = factories.PersonFactory(organisation=organisation)
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_edit_by_superuser(self):
        user = factories.SuperUserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(id=100, account=account)
        person = factories.PersonFactory(organisation=organisation)
        url = self.reverse('management:persons_edit', pk=person.pk)
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
        organisation = factories.OrganisationFactory(account=account)
        person = factories.PersonFactory(organisation=organisation)
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
