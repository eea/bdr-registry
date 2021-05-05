from django.conf import settings
from django.contrib.auth import models as auth_models
import factory
from factory import fuzzy, django

from django.db.models import signals
from .base import mute_signals
from bdr_registry import models


text_fuzzer = fuzzy.FuzzyText()
email_fuzzer = fuzzy.FuzzyText(length=6, suffix='@eaudeweb.ro')
integer_fuzzer = fuzzy.FuzzyInteger(1000)


class UserFactory(django.DjangoModelFactory):

    class Meta:
        model = auth_models.User
        django_get_or_create = ('username', 'email')

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

    @factory.post_generation
    def set_group(self, create, extracted, **kwargs):
        group = BDRGroupFactory()
        self.groups.add(group)


class BDRGroupFactory(django.DjangoModelFactory):

    class Meta:
        model = auth_models.Group

    name = settings.BDR_HELPDESK_GROUP


class AccountFactory(django.DjangoModelFactory):

    class Meta:
        model = models.Account
        django_get_or_create = ('uid',)

    uid = fuzzy.FuzzyText()


class CountryFactory(django.DjangoModelFactory):

    class Meta:
        model = models.Country
        django_get_or_create = ('name', 'code')

    name = 'Romania'
    code = 'RO'


class EmailTemplateFactory(django.DjangoModelFactory):

    class Meta:
        model = models.EmailTemplate
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()


class ObligationFactory(django.DjangoModelFactory):

    class Meta:
        model = models.Obligation
        django_get_or_create = ('name', 'code')

    name = fuzzy.FuzzyText()
    code = factory.Iterator(['ods', 'fgas'])
    reportek_slug = fuzzy.FuzzyText()
    email_template = factory.SubFactory(EmailTemplateFactory)


class SiteConfigurationFactory(django.DjangoModelFactory):

    class Meta:
        model = models.SiteConfiguration

    reporting_year = 2015
    self_register_email_template = factory.SubFactory(EmailTemplateFactory)


@mute_signals(signals.post_save)
class CompanyFactory(django.DjangoModelFactory):

    class Meta:
        model = models.Company
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()
    addr_street = fuzzy.FuzzyText()
    addr_place1 = fuzzy.FuzzyText()
    addr_postalcode = fuzzy.FuzzyInteger(99999)
    country = factory.SubFactory(CountryFactory)
    obligation = factory.SubFactory(ObligationFactory)
    vat_number = fuzzy.FuzzyText()

    @factory.post_generation
    def people(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for person in extracted:
                self.people.add(person)


class PersonFactory(django.DjangoModelFactory):

    class Meta:
        model = models.Person
        django_get_or_create = ('email',)

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

    class Meta:
        model = models.Comment

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
        'obligation': '1',
        'vat_number': '1'
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
