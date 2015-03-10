
from .base import BaseWebTest
from bdr_management.tests import factories
from bdr_registry.models import Comment


class CommentManagementTests(BaseWebTest):

    def test_comment_add_by_staff_user(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Comment, text='hey')

    def test_comment_add_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username)
        self.assertRedirects(resp,
                             self.reverse('management:companies_view',
                                          pk=company.pk))
        self.assertObjectInDatabase(Comment, text='hey')

    def test_comment_add_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username)
        self.assertRedirects(resp,
                             self.reverse('management:companies_view',
                                          pk=company.pk))
        self.assertObjectInDatabase(Comment, text='hey')

    def test_comment_add_by_anonymous(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        url = self.reverse('management:comment_add', pk=company.pk)
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        resp = self.app.post(url, {'text': 'hey'}, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Comment, text='hey')

    def test_comment_delete_by_staff(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectInDatabase(Comment, pk=comment.pk)

    def test_comment_delete_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        self.assertObjectInDatabase(Comment, pk=comment.pk)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('management:companies_view',
                                   pk=company.pk)
        self.assertRedirects(resp, success_url)
        self.assertObjectNotInDatabase(Comment, pk=company.pk)

    def test_comment_delete_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('management:companies_view',
                                   pk=company.pk)
        self.assertRedirects(resp, success_url)
        self.assertObjectNotInDatabase(Comment, pk=company.pk)

    def test_comment_delete_by_anonymous(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('management:comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectInDatabase(Comment, pk=comment.pk)


class CommentTests(BaseWebTest):

    def test_comment_add_by_staff_user(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Comment, text='hey')

    def test_comment_add_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username)
        self.assertRedirects(resp, self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Comment, text='hey')

    def test_comment_add_by_superuser(self):
        factories.SiteConfigurationFactory()
        user = factories.SuperUserFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username)
        self.assertRedirects(resp, self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Comment, text='hey')

    def test_comment_add_by_owner(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        resp = self.app.post(url, {'text': 'hey'}, user=user.username)
        self.assertRedirects(resp, self.reverse('company', pk=company.pk))
        self.assertObjectInDatabase(Comment, text='hey')

    def test_comment_add_by_anonymous(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        url = self.reverse('comment_add', pk=company.pk)
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        resp = self.app.post(url, {'text': 'hey'}, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectNotInDatabase(Comment, text='hey')

    def test_comment_delete_by_staff_user(self):
        factories.SiteConfigurationFactory()
        user = factories.StaffUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_comment_delete_by_bdr_group(self):
        factories.SiteConfigurationFactory()
        user = factories.BDRGroupUserFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)
        self.assertObjectNotInDatabase(Comment, pk=comment.pk)

    def test_comment_delete_by_owner(self):
        factories.SiteConfigurationFactory()
        user = factories.UserFactory()
        account = factories.AccountFactory(uid=user.username)
        company = factories.CompanyFactory(account=account)
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, user=user.username)
        success_url = self.reverse('company', pk=company.pk)
        self.assertRedirects(resp, success_url)
        self.assertObjectNotInDatabase(Comment, pk=comment.pk)

    def test_comment_delete_by_anonymous(self):
        factories.SiteConfigurationFactory()
        company = factories.CompanyFactory()
        comment = factories.CommentFactory(company=company)
        url = self.reverse('comment_delete', pk=company.pk,
                           comment_pk=comment.pk)
        resp = self.app.delete(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)
        self.assertObjectInDatabase(Comment, pk=comment.pk)
