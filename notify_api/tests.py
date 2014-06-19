from httplib import FORBIDDEN, OK, NOT_FOUND

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy
from model_mommy.generators import gen_email

from bdr_registry.models import ApiKey, Account, Company, Person


class NotifyApiAddFileTests(TestCase):

    def setUp(self):
        self.api_key = mommy.make(ApiKey).key
        account = mommy.make(Account)
        self.account = account.uid
        self.company = mommy.make(Company, account=account)
        self.must_receive = [
            p.email for p in mommy.make(Person, 2, company=self.company)]
        self.must_not_receive = [
            p.email for p in mommy.make(Person, 2, company=mommy.make(Company))]

    def test_add_file_without_api_key(self):
        url = reverse('add_file',
                      kwargs={'account': self.account})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_add_file_with_invalid_api_key(self):
        url = reverse('add_file',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': 'invalid'})

        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_add_file_with_valid_api_key(self):
        url = reverse('add_file',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, OK)

    def test_add_file_with_inexistent_account(self):
        account = mommy.prepare(Account).uid
        url = reverse('add_file',
                      kwargs={'account': account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, NOT_FOUND)

    def test_add_file_sends_to_correct_recipients(self):
        url = reverse('add_file',
                      kwargs={'account': self.account})
        self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(len(mail.outbox), 1)
        self.assertItemsEqual(self.must_receive, mail.outbox[0].to)


class NotifyApiAddFeedbackTests(TestCase):

    def setUp(self):
        self.api_key = mommy.make(ApiKey).key
        account = mommy.make(Account)
        self.account = account.uid
        self.company = mommy.make(Company, account=account)
        self.must_receive = [
            p.email for p in mommy.make(Person, 2, company=self.company)]
        self.must_not_receive = [
            p.email for p in mommy.make(Person, 2, company=mommy.make(Company))]

    def test_add_feedback_without_api_key(self):
        url = reverse('add_feedback',
                      kwargs={'account': self.account})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_add_feedback_with_invalid_api_key(self):
        url = reverse('add_feedback',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': 'invalid'})

        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_add_feedback_with_valid_api_key(self):
        url = reverse('add_feedback',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, OK)

    def test_add_feedback_with_inexistent_account(self):
        account = mommy.prepare(Account).uid
        url = reverse('add_feedback',
                      kwargs={'account': account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, NOT_FOUND)

    def test_add_feedback_sends_to_correct_recipients(self):
        url = reverse('add_feedback',
                      kwargs={'account': self.account})
        self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(len(mail.outbox), 1)
        self.assertItemsEqual(self.must_receive, mail.outbox[0].to)
        

class NotifyApiReleaseTests(TestCase):

    def setUp(self):
        self.api_key = mommy.make(ApiKey).key
        account = mommy.make(Account)
        self.account = account.uid
        self.company = mommy.make(Company, account=account)

        bdr_group = mommy.make(Group, name=settings.BDR_HELPDESK_GROUP)
        u1 = mommy.make(User, groups=(bdr_group,), email=gen_email())
        u2 = mommy.make(User, groups=(bdr_group,), email=gen_email())
        u3 = mommy.make(User, groups=(bdr_group,), email=gen_email())
        u3.obligations.add(self.company.obligation)
        u4 = mommy.make(User, groups=(bdr_group,), email=gen_email())
        u4.obligations.add(self.company.obligation)
        u5 = mommy.make(User, email=gen_email())
        u5.obligations.add(self.company.obligation)
        u6 = mommy.make(User, email=gen_email())
        u6.obligations.add(self.company.obligation)

        self.must_receive = [u3.email, u4.email]
        self.must_not_receive = [u1.email, u2.email, u5.email, u6.email]

    def test_release_without_api_key(self):
        url = reverse('release',
                      kwargs={'account': self.account})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_release_with_invalid_api_key(self):
        url = reverse('release',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': 'invalid'})

        self.assertEqual(resp.status_code, FORBIDDEN)

    def test_release_with_valid_api_key(self):
        url = reverse('release',
                      kwargs={'account': self.account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, OK)

    def test_release_with_inexistent_account(self):
        account = mommy.prepare(Account).uid
        url = reverse('release',
                      kwargs={'account': account})
        resp = self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(resp.status_code, NOT_FOUND)

    def test_release_sends_to_correct_recipients(self):
        url = reverse('release',
                      kwargs={'account': self.account})
        self.client.post(url, {'apiKey': self.api_key})

        self.assertEqual(len(mail.outbox), 1)
        self.assertItemsEqual(self.must_receive, mail.outbox[0].to)
