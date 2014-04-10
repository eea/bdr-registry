
from .base import BaseWebTest
from bdr_management.tests import factories


class OrganisationActionsTests(BaseWebTest):

    def test_reset_password_get_with_account(self):
        organisation = factories.OrganisationWithAccountFactory()

