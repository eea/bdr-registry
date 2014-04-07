
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationTests(BaseWebTest):

    def test_organisations_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:organisations'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisations_view_by_anonymous(self):
        resp = self.app.get(self.reverse('management:organisations'))
        resp.follow()

    def test_organisation_view_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view',
                           pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_anonymous_(self):
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view',
                           pk=organisation.pk)
        resp = self.app.get(url, user=None)
        resp.follow()

    def test_organisation_view_update_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        organisation = factories.OrganisationFactory(account=account)
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_update_by_anonymous(self):
        user = factories.UserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        resp.follow()

    def test_organisation_view_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_update_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('organisation', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

