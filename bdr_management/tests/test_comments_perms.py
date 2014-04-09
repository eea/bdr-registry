
from .base import BaseWebTest
from bdr_management.tests import factories


class CommentTests(BaseWebTest):

    def test_management_comment_add_by_staff_user(self):
        user = factories.StaffUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:comment_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_management_comment_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:comment_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_management_comment_add_by_superuser(self):
        user = factories.SuperUserFactory()
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:comment_add', pk=organisation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_management_comment_add_anonymous(self):
        organisation = factories.OrganisationFactory()
        url = self.reverse('management:comment_add', pk=organisation.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))
