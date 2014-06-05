from django.conf import settings
import factory
from factory import fuzzy, django

from django.db.models import signals
from .base import mute_signals


text_fuzzer = fuzzy.FuzzyText()
email_fuzzer = fuzzy.FuzzyText(length=6, suffix='@eaudeweb.ro')
integer_fuzzer = fuzzy.FuzzyInteger(1000)


class UserFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'auth.User'
    FACTORY_DJANGO_GET_OR_CREATE = ('username', 'email')

    first_name = factory.Sequence(lambda n: 'user_%d' % n)
    last_name = factory.Sequence(lambda n: 'user_%d' % n)
    username = factory.Sequence(lambda n: 'user_%d' % n)
    email = factory.Sequence(lambda n: 'user_%d@eaudeweb.ro' % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)

    @factory.post_generation
    def obligations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for obligation in extracted:
                self.obligations.add(obligation)


class StaffUserFactory(UserFactory):

    username = factory.Sequence(lambda n: 'staff_%d' % n)
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


class EmailTemplateFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'post_office.EmailTemplate'
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = fuzzy.FuzzyText()


class ObligationFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Obligation'
    FACTORY_DJANGO_GET_OR_CREATE = ('name', 'code')

    name = fuzzy.FuzzyText()
    code = factory.Iterator(['ods', 'fgas'])
    email_template = factory.SubFactory(EmailTemplateFactory)


@mute_signals(signals.post_save)
class CompanyFactory(django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Company'
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = fuzzy.FuzzyText()
    addr_street = fuzzy.FuzzyText()
    addr_place1 = fuzzy.FuzzyText()
    addr_postalcode = fuzzy.FuzzyInteger(99999)
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


def company_form():
    return {
        'name': text_fuzzer.fuzz(),
        'addr_street': text_fuzzer.fuzz(),
        'addr_place1': CountryFactory().name,
        'addr_postalcode': text_fuzzer.fuzz(),
        'addr_place2': text_fuzzer.fuzz(),
        'country': '1',
        'obligation': '1'
    }.copy()


def person_form(company_pk=integer_fuzzer.fuzz()):
    return {
        'title': "Mr.",
        'first_name': text_fuzzer.fuzz(),
        'family_name': text_fuzzer.fuzz(),
        'email': email_fuzzer.fuzz(),
        'phone': text_fuzzer.fuzz(),
        'company': company_pk
    }.copy()


def company_with_person_form():
    form = company_form()
    form.update(person_form())
    return form

