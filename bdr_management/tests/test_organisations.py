
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationActionsTests(BaseWebTest):

    def test_reset_password_get_with_account(self):
        org = factories.OrganisationWithAccountFactory()
        url = self.reverse('management:reset_password', pk=org.pk)
        resp = self.app.get(url, user='admin')
        self.assertEqual(200, resp.status_int)
        self.assertEqual('Reset password for %s' % org.name,
                         resp.pyquery.find('h1').text())

