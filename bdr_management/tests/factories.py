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


class CountryFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Country'
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'code')

    name = 'Romania'
    code = 'RO'


@mute_signals(signals.post_save)
class OrganisationFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Organisation'
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = fuzzy.FuzzyText()
    country = factory.SubFactory(CountryFactory)
