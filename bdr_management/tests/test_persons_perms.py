
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationTests(BaseWebTest):

    def setUp(self):
        self.staff = factories.StaffUserFactory()

    def test_organisations_view_by_staff_user(self):
        resp = self.app.get(self.reverse('management:persons'),
                            user=self.staff.username)
        self.assertEqual(200, resp.status_int)

    def test_organisations_view_by_anonymous_user_fail(self):
        resp = self.app.get(self.reverse('management:persons'))
        resp.follow()
