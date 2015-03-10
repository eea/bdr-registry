from django.core import mail

from bdr_management.tests import base, factories
from bdr_registry.views import send_notification_email


class BackendTests(base.BaseWebTest):

    def test_self_register_mail_to_correct_users(self):
        factories.SiteConfigurationFactory()
        obligation1 = factories.ObligationFactory()
        obligation2 = factories.ObligationFactory()
        obligation3 = factories.ObligationFactory()
        person = factories.PersonFactory()
        company = factories.CompanyFactory(obligation=obligation2, people=(person,))
        bdr_group = factories.BDRGroupFactory()

        user1 = factories.StaffUserFactory()
        user2 = factories.StaffUserFactory(groups=(bdr_group,))
        user3 = factories.StaffUserFactory(groups=(bdr_group,),
                                           obligations=(obligation1, obligation2))
        user4 = factories.StaffUserFactory(groups=(bdr_group,),
                                           obligations=(obligation1, obligation3))

        send_notification_email({'company': company, 'person': person})

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user3.email])
