from django.test import Client
import json

from .base import BaseWebTest
from bdr_management.tests import factories


class ObligationManagementTests(BaseWebTest):

    def test_obligations_list_by_anonymous(self):
        url = self.reverse('management:obligations')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligations_list_by_staff_user(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligations_list_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligations_list_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_anonymous(self):
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_view_by_staff_user(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username,)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_view_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_add_by_staff(self):
        user = factories.StaffUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_add_by_anonymous(self):
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_add_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        params={
            'name': 'test',
            'code': 'test',
            'reportek_slug': 'test',
            'email_template': factories.EmailTemplateFactory().pk,
        }
        resp = self.app.post(url, user=user.username, params=params)
        self.assertEqual(302, resp.status_int)

    def test_obligation_add_by_superuser(self):
        user = factories.SuperUserFactory()
        url = self.reverse('management:obligations_add')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)
        params={
            'name': 'test',
            'code': 'test',
            'reportek_slug': 'test',
            'email_template': factories.EmailTemplateFactory().pk
        }
        resp = self.app.post(url, user=user.username, params=params)
        self.assertEqual(302, resp.status_int)


    def test_obligation_update_by_staff(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_update_by_anonymous(self):
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_update_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

    def test_obligation_delete_by_staff(self):
        user = factories.StaffUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_delete_by_anonymous(self):
        user = factories.UserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username, expect_errors=True)
        self.assertEqual(resp.status_int, 403)

    def test_obligation_delete_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:obligations'))

    def test_obligation_delete_get(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.get(url, user=user.username)
        self.assertEqual(resp.status_int, 200)

    def test_obligation_delete_by_superuser(self):
        user = factories.SuperUserFactory()
        obligation = factories.ObligationFactory()
        url = self.reverse('management:obligation_delete', pk=obligation.pk)
        resp = self.app.delete(url, user=user.username)
        self.assertRedirects(resp, self.reverse('management:obligations'))

    def test_obligation_after_update_by_bdr_group(self):
        user = factories.BDRGroupUserFactory()
        obligation = factories.ObligationFactory()
        obligation.admins = [user]
        url = self.reverse('management:obligation_edit',
                           **{'pk': obligation.pk})
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

        #modify the obligation
        params={
            'name': obligation.name,
            'code': obligation.code,
            'reportek_slug': obligation.reportek_slug,
            'email_template': obligation.email_template.id,
            'bcc': obligation.bcc,
            'admins': [u.id for u in obligation.admins.all()]
        }
        resp = self.app.post(url,
                             params=params,
                             user=user.username
        )

        #render obligation page
        url = self.reverse('management:obligation_view',
                           **{'pk': obligation.pk})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], url)

        #user has only one obligation
        user_obligations = user.obligations.values()
        self.assertEqual(len(user_obligations), 1)

        #set user password
        user.set_password('q')
        user.save()

        #render obligations page
        url = self.reverse('management:obligations')
        resp = self.app.get(url, user=user.username)
        self.assertEqual(200, resp.status_int)

        #login user and make the ajax request
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        logged_in = client.login(username=user.username, password='q')
        self.assertEqual(logged_in, True)

        url = self.reverse('management:obligations_filter')
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        data = {'sColumns': 'id,name'}
        resp = client.get(url, data, **kwargs)
        self.assertEqual(resp.status_code, 200)

        # filter obligations

        url = self.reverse('management:obligations_filter')
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        data = {'sColumns': 'id,name', 'search': 'test', 'order_by': 'name'}
        resp = client.get(url, data, **kwargs)
        self.assertEqual(resp.status_code, 200)

        #make sure the user's obligation id is present in returned data
        data = json.loads(resp.content)
        ids = [row[0] for row in data['aaData']]
        self.assertEqual(user_obligations[0]['id'] in ids, True)
