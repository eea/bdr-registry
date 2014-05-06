from django.conf import settings
import factory
from factory import fuzzy, django

from django.db.models import signals
from .base import mute_signals


class UserFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'auth.User'
    FACTORY_DJANGO_GET_OR_CREATE = ('username', 'email')

    first_name = factory.Sequence(lambda n: 'user_%d' % n)
    last_name = factory.Sequence(lambda n: 'user_%d' % n)
    username = factory.Sequence(lambda n: 'user_%d' % n)
    email = factory.Sequence(lambda n: 'user_%d@eaudeweb.ro' % n)


class StaffUserFactory(UserFactory):

    username = 'staff'
    is_staff = True


class SuperUserFactory(UserFactory):

    username = 'admin'
    is_staff = True
    is_superuser = True


class BDRGroupUserFactory(UserFactory):

    is_staff = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        group = BDRGroupFactory()
        user = super(BDRGroupUserFactory, cls)._prepare(create, **kwargs)
        user.groups.add(group)
        return user


class BDRGroupFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'auth.Group'

    name = settings.BDR_HELPDESK_GROUP


class AccountFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Account'
    FACTORY_DJANGO_GET_OR_CREATE = ('uid',)

    uid = fuzzy.FuzzyText()


class CountryFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Country'
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'code')

    name = 'Romania'
    code = 'RO'


class ObligationFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Obligation'
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'code')

    name = fuzzy.FuzzyText()
    code = factory.Iterator(['ods', 'fgas'])


@mute_signals(signals.post_save)
class CompanyFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Company'
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = fuzzy.FuzzyText()
    country = factory.SubFactory(CountryFactory)
    obligation = factory.SubFactory(ObligationFactory)

    @factory.post_generation
    def people(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for person in extracted:
                self.people.add(person)


class PersonFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Person'
    FACTORY_DJANGO_GET_OR_CREATE = ('email',)

    first_name = fuzzy.FuzzyText()
    family_name = fuzzy.FuzzyText()

    email = factory.Sequence(lambda n: 'person_%d@eaudeweb.ro' % n)
    phone = fuzzy.FuzzyText()
    company = factory.SubFactory(CompanyFactory)


class CompanyWithAccountFactory(CompanyFactory):

    person1 = factory.RelatedFactory(PersonFactory, 'company')

    @factory.post_generation
    def account(self, create, extracted, **kwargs):
        if not create:
            return
        user = extracted or SuperUserFactory()
        self.account = AccountFactory(uid=user.username)


class CommentFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Comment'

    text = fuzzy.FuzzyText()
    company = factory.SubFactory(CompanyFactory)


