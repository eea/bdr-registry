
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationTests(BaseWebTest):

    def test_organisations_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        resp = self.app.get(self.reverse('management:organisations'),
                            user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisations_view_by_anonymous_user_fail(self):
        resp = self.app.get(self.reverse('management:organisations'))
        resp.follow()

    def test_organisation_view_by_staff(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view',
                           pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_organisation_view_by_staff_fails(self):
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:organisations_view',
                           pk=organisation.pk)
        resp = self.app.get(url, user=None)
        resp.follow()
