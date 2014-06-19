from httplib import FORBIDDEN
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy
from bdr_registry.models import ApiKey


class NotifyApiTest(TestCase):

    def setUp(self):
        self.api_key = mommy.make(ApiKey)

    def test_add_file_without_api_key(self):
        resp = self.client.post(reverse('add_file'))
        self.assertEqual(resp.status_code, FORBIDDEN)
