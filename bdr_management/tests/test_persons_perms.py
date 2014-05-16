
from .base import BaseWebTest
from bdr_management.tests import factories
from bdr_registry.models import Person


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

    def test_person_add_post_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, user=user, params=form)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 0)

    def test_person_add_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_post_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, params=form)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 0)

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_post_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('management:companies_view',
                                                **{'pk': company.pk}))
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.first().company, company)

    def test_person_add_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_post_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:persons_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('management:companies_view',
                                                **{'pk': company.pk}))
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.first().company.pk, company.pk)

    def test_add_person_to_missing_company(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:persons_add', pk=123)
        form = factories.person_form()

        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 404)

        resp = self.app.post(url, params=form, user=user.username,
                             expect_errors=True)
        self.assertEqual(resp.status_int, 404)

    def test_person_update_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_post_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(person, Person.objects.first())
        self.assertEqual(person.first_name, new_person.first_name)

    def test_person_update_by_anonymous(self):
        user = factories.UserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_post_by_anonymous(self):
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.post(url, params=form)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(person, Person.objects.first())
        self.assertEqual(person.first_name, new_person.first_name)

    def test_person_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        
    def test_person_update_post_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person = factories.PersonFactory()
        form = factories.person_form()
        factories.CompanyFactory(pk=form['company'])
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('management:persons_view',
                                                **{'pk': person.pk}))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(new_person.first_name, form['first_name'])
        self.assertEqual(new_person.company.pk, form['company'])

    def test_person_update_by_superuser(self):
        user = factories.SuperUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_post_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        person = factories.PersonFactory()
        form = factories.person_form(company_pk=company.pk)
        url = self.reverse('management:persons_edit', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('management:persons_view',
                                                **{'pk': person.pk}))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(new_person.first_name, form['first_name'])
        self.assertEqual(new_person.company.pk, form['company'])

    def test_person_delete_by_staff(self):
        user = factories.StaffUserFactory()
        person1 = factories.PersonFactory()
        factories.PersonFactory(company=person1.company)
        url = self.reverse('management:persons_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_anonymous(self):
        user = factories.UserFactory()
        person1 = factories.PersonFactory()
        factories.PersonFactory(company=person1.company)
        url = self.reverse('management:persons_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person1 = factories.PersonFactory()
        factories.PersonFactory(company=person1.company)
        url = self.reverse('management:persons_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, '/management/persons')

    def test_person_delete_by_bdr_superuser(self):
        user = factories.SuperUserFactory()
        person1 = factories.PersonFactory()
        factories.PersonFactory(company=person1.company)
        url = self.reverse('management:persons_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, '/management/persons')

    def test_delete_last_person(self):
        company = factories.CompanyFactory()
        person = factories.PersonFactory(company=company)
        url = self.reverse('management:persons_delete', pk=person.pk)
        resp = self.app.delete(url, user=factories.SuperUserFactory())
        self.assertRedirects(resp, self.reverse('management:persons_view',
                                                pk=person.pk))
        resp = resp.follow()
        expected_messages = [
            u'Cannot delete the only designated company reporter '
            u'for "%s"' % person.company]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)

    def test_delete_missing_person(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:persons_delete', pk=123)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 404)


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

    def test_person_add_post_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('person_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 0)

    def test_person_add_by_anonymous(self):
        company = factories.CompanyFactory(id=100)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_add_post_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('person_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, params=form)
        self.assertRedirects(resp, self.get_login_for_url(url))
        self.assertEqual(Person.objects.count(), 0)

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory(id=100)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_post_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('person_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, user=user.username, params=form)
        self.assertRedirects(resp, self.reverse('company',
                                                **{'pk': company.pk}))
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.first().company.pk, company.pk)

    def test_person_add_by_owner(self):
        user = factories.BDRGroupUserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(id=100, account=account)
        url = self.reverse('person_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_add_post_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('person_add', pk=company.pk)
        form = factories.person_form()
        resp = self.app.post(url, user=user.username, params=form)
        self.assertRedirects(resp, self.reverse('company',
                                                **{'pk': company.pk}))
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.first().company.pk, company.pk)

    def test_add_person_to_missing_company(self):
        user = factories.SuperUserFactory()
        url = self.reverse('person_add', pk=123)
        form = factories.person_form()

        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 404)

        resp = self.app.post(url, params=form, user=user.username,
                             expect_errors=True)
        self.assertEqual(resp.status_int, 404)

    def test_person_update_by_anonymous(self):
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_post_by_anonymous(self):
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.post(url, params=form)
        self.assertRedirects(resp, self.get_login_for_url(url))
        new_person = Person.objects.first()
        self.assertNotEqual(new_person.first_name, form['first_name'])
        self.assertEqual(new_person.first_name, person.first_name)

    def test_person_update_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_update_post_by_staff(self):
        user = factories.StaffUserFactory()
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))
        new_person = Person.objects.first()
        self.assertNotEqual(new_person.first_name, form['first_name'])
        self.assertEqual(new_person.first_name, person.first_name)

    def test_person_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_post_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        person = factories.PersonFactory(company=company)
        form = factories.person_form(company_pk=company.pk)
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('person',
                                                **{'pk': person.pk}))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(new_person.first_name, form['first_name'])
        self.assertEqual(person.company, new_person.company)

    def test_person_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_post_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('person',
                                                **{'pk': person.pk}))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(new_person.first_name, form['first_name'])
        self.assertEqual(person.company, new_person.company)

    def test_person_update_by_superuser(self):
        user = factories.SuperUserFactory()
        person = factories.PersonFactory()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_person_update_post_by_superuser(self):
        user = factories.SuperUserFactory()
        person = factories.PersonFactory()
        form = factories.person_form()
        url = self.reverse('person_update', pk=person.pk)
        resp = self.app.post(url, params=form, user=user.username)
        self.assertRedirects(resp, self.reverse('person',
                                                **{'pk': person.pk}))
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.first()
        self.assertEqual(new_person.first_name, form['first_name'])
        self.assertEqual(person.company, new_person.company)

    def test_person_delete_by_staff_user(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        person1 = factories.PersonFactory(company=company)
        factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_person_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        person1 = factories.PersonFactory(company=company)
        factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_person_delete_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        person1 = factories.PersonFactory(company=company)
        factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person1.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_person_delete_by_anonymous(self):
        company = factories.CompanyFactory()
        person1 = factories.PersonFactory(company=company)
        factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person1.pk)
        resp = self.app.delete(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_delete_last_person(self):
        company = factories.CompanyFactory()
        person = factories.PersonFactory(company=company)
        url = self.reverse('person_delete', pk=person.pk)
        resp = self.app.delete(url, user=factories.SuperUserFactory())
        self.assertRedirects(resp, self.reverse('person', pk=person.pk))
        resp = resp.follow()
        expected_messages = [
            u'Cannot delete the only designated company reporter '
            u'for "%s"' % person.company]
        actual_messages = map(str, resp.context['messages'])
        self.assertItemsEqual(expected_messages, actual_messages)
