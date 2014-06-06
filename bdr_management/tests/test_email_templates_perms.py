
from .base import BaseWebTest
from bdr_management.tests import factories


class EmailTemplateManagementTests(BaseWebTest):

    def test_email_templates_list_by_anonymous(self):
        url = self.reverse('management:email_templates')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_email_templates_list_by_staff_user(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:email_templates')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_templates_list_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:email_templates')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_templates_list_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:email_templates')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_view_by_anonymous(self):
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_view',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_email_template_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_view',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username,)
        self.assertEqual(200, resp.status_int)

    def test_email_template_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_view',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_view_by_superuser(self):
        user = factories.SuperUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_view',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_add_by_staff(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:email_templates_add')
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_email_template_add_by_anonymous(self):
        url = self.reverse('management:email_templates_add')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_person_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:email_templates_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_add_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:email_templates_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_update_by_staff(self):
        user = factories.StaffUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_edit',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_email_template_update_by_anonymous(self):
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_edit',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_email_template_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_edit',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_update_by_superuser(self):
        user = factories.SuperUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_edit',
                           **{'pk': email_template.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_email_template_delete_by_staff(self):
        user = factories.StaffUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_delete', pk=email_template.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_person_delete_by_anonymous(self):
        user = factories.UserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_delete', pk=email_template.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_person_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_delete', pk=email_template.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:email_templates'))

    def test_person_delete_by_superuser(self):
        user = factories.SuperUserFactory()
        email_template = factories.EmailTemplateFactory()
        url = self.reverse('management:email_template_delete', pk=email_template.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:email_templates'))
