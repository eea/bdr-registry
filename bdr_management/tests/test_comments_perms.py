
from .base import BaseWebTest
from bdr_management.tests import factories


class CommentManagementTests(BaseWebTest):

    def test_comment_add_by_staff_user(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_comment_add_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_comment_add_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_delete_by_staff(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('management:organisations_view',
                                   pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_comment_delete_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('management:organisations_view',
                                   pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_comment_delete_by_anonymous(self):
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url)
        self.assertRedirects(resp, self.get_login_for_url(url))


class CommentTests(BaseWebTest):

    def test_comment_add_by_staff_user(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_comment_add_by_superuser(self):
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_comment_add_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_comment_add_by_anonymous(self):
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_delete_by_staff_user(self):
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.get_login_for_url(url))

    def test_comment_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_comment_delete_by_owner(self):
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)

    def test_comment_delete_by_anonymous(self):
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url)
        self.assertRedirects(resp, self.get_login_for_url(url))
