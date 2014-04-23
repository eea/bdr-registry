import random
import string

from django.db import models
from django.core.urlresolvers import reverse
import local
from django.utils.translation import ugettext_lazy as _


def generate_key(size=20):
    crypto_random = random.SystemRandom()
    vocabulary = string.ascii_lowercase + string.digits
    return ''.join(crypto_random.choice(vocabulary) for c in range(size))


class ApiKey(models.Model):

    key = models.CharField(max_length=255, default=generate_key)
    comment = models.CharField(max_length=255)

    def __unicode__(self):
        return self.comment


class Country(models.Model):

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    class Meta(object):
        verbose_name_plural = 'Countries'

    def __unicode__(self):
        return self.name


class Obligation(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    reportek_slug = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def generate_account_id(self):
        query = (NextAccountId.objects.select_for_update()
                 .filter(obligation=self))
        try:
            next_row = query[0]
        except IndexError:
            next_row = NextAccountId(obligation=self, next_id=1)
            next_row.save()
        value = next_row.next_id
        next_row.next_id += 1
        next_row.save()
        return value


class AccountManager(models.Manager):

    def create_for_obligation(self, obligation):
        next_id = obligation.generate_account_id()
        uid = u"{o.code}{next_id}".format(o=obligation, next_id=next_id)
        return self.create(uid=uid)


class Account(models.Model):

    uid = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.uid

    def set_random_password(self):
        self.password = generate_key(size=8)
        self.save()

    objects = AccountManager()


class NextAccountId(models.Model):

    next_id = models.IntegerField()
    obligation = models.OneToOneField(Obligation, null=True, blank=True)

    def __unicode__(self):
        return u"next_id={p.next_id} ({p.obligation.name})".format(p=self)


class Company(models.Model):

    EORI_LABEL = _('Economic Operators Registration and Identification number (EORI)')

    name = models.CharField(_('Company name'), max_length=255)
    date_registered = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    addr_street = models.CharField(_('Street and number'), max_length=255)
    addr_place1 = models.CharField(_('Municipality'), max_length=255)
    addr_postalcode = models.CharField(_('Postal code'), max_length=255)
    addr_place2 = models.CharField(_('Region'),
                            max_length=255, null=True, blank=True)
    eori = models.CharField(_('EORI number'), help_text=EORI_LABEL,
                            max_length=17, null=True, blank=True)
    vat_number = models.CharField(_('VAT number'),
                            max_length=17, null=True, blank=True)
    country = models.ForeignKey(Country)
    obligation = models.ForeignKey(Obligation, null=True, blank=True)
    account = models.OneToOneField(Account, null=True, blank=True,
                                   related_name='company')
    website = models.URLField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('company', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name


def organisation_loaded(instance, **extra):
    instance._initial_name = '' if instance.pk is None else instance.name


def organisation_saved(instance, **extra):
    if instance._initial_name != instance.name:
        try:
            user = local.get_request().user
        except AttributeError:
            user = None
        if user is not None and user.is_authenticated():
            user_id = user.id
        else:
            user_id = None
        instance.namehistory.create(name=instance.name, user_id=user_id)


models.signals.post_init.connect(organisation_loaded, sender=Company)
models.signals.post_save.connect(organisation_saved, sender=Company)


class CompanyNameHistory(models.Model):

    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, related_name='namehistory')
    user = models.ForeignKey('auth.User', null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{h.name} {h.time} {h.user}".format(h=self)


class Person(models.Model):

    title = models.CharField(_('Title'), max_length=255, null=True, blank=True)
    family_name = models.CharField(_('Family name'), max_length=255)
    first_name = models.CharField(_('First name'), max_length=255)

    email = models.EmailField(_('Email address'))

    phone = models.CharField(_('Telephone'), max_length=255)
    phone2 = models.CharField(_('Telephone 2'),
                            max_length=255, null=True, blank=True)
    phone3 = models.CharField(_('Telephone 3'),
                            max_length=255, null=True, blank=True)
    fax = models.CharField(_('Fax'),
                           max_length=255, null=True, blank=True)

    company = models.ForeignKey(Company, related_name='people')

    @property
    def formal_name(self):
        return u"{p.title} {p.first_name} {p.family_name}".format(p=self)

    def __unicode__(self):
        return u"{p.first_name} {p.family_name} <{p.email}>".format(p=self)


class Comment(models.Model):
    text = models.TextField(_('Comment'))
    created = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company,
                                related_name='comments')

    def __unicode__(self):
        return self.created.strftime('%d %B %Y')
