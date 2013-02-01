import random
import string
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import local


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

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Obligation(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    reportek_slug = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def generate_account_id(self):
        query = NextAccountId.objects.select_for_update()
        next_account_id = query.filter(obligation=self)[0]
        value = next_account_id.next_id
        next_account_id.next_id += 1
        next_account_id.save()
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
        try:
            org_name = self.organisation.name
        except Organisation.DoesNotExist:
            org_name = None
        return u"uid={p.uid} ({org_name})".format(p=self, org_name=org_name)

    def set_random_password(self):
        self.password = generate_key(size=8)
        self.save()

    objects = AccountManager()


class NextAccountId(models.Model):

    next_id = models.IntegerField()
    obligation = models.OneToOneField(Obligation, null=True, blank=True)

    def __unicode__(self):
        return u"next_id={p.next_id} ({p.obligation.name})".format(p=self)


class Organisation(models.Model):

    name = models.CharField(max_length=255,
                            verbose_name="Company name")
    date_registered = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    addr_street = models.CharField(max_length=255,
                                   verbose_name="Street and nr")
    addr_place1 = models.CharField(max_length=255,
                                   verbose_name="Place 1 / Municipality")
    addr_postalcode = models.CharField(max_length=255,
                                   verbose_name="Postal code")
    addr_place2 = models.CharField(max_length=255,
                                   verbose_name="Place 2 / Region",
                                   null=True, blank=True)
    vat_number = models.CharField(max_length=17, verbose_name="VAT number",
                                  null=True, blank=True)
    country = models.ForeignKey(Country)
    obligation = models.ForeignKey(Obligation, null=True, blank=True)
    account = models.OneToOneField(Account, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('organisation', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name


def organisation_loaded(instance, **extra):
    instance._initial_name = '' if instance.pk is None else instance.name


def organisation_saved(instance, **extra):
    if instance._initial_name != instance.name:
        user = local.get_request().user
        if user is not None and user.is_authenticated():
            user_id = user.id
        else:
            user_id = None
        instance.namehistory.create(name=instance.name, user_id=user_id)


models.signals.post_init.connect(organisation_loaded, sender=Organisation)
models.signals.post_save.connect(organisation_saved, sender=Organisation)


class OrganisationNameHistory(models.Model):

    name = models.CharField(max_length=255)
    organisation = models.ForeignKey(Organisation, related_name='namehistory')
    user = models.ForeignKey('auth.User', null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{h.name} {h.time} {h.user}".format(h=self)


class Person(models.Model):

    title = models.CharField(max_length=255, verbose_name="Title")
    family_name = models.CharField(max_length=255, verbose_name="Family name")
    first_name = models.CharField(max_length=255, verbose_name="First name")

    email = models.EmailField(verbose_name="Email address")
    email2 = models.EmailField(verbose_name="Email address 2",
                               null=True, blank=True)

    phone = models.CharField(max_length=255, verbose_name="Telephone")
    phone2 = models.CharField(max_length=255, verbose_name="Telephone 2",
                              null=True, blank=True)
    phone3 = models.CharField(max_length=255, verbose_name="Telephone 3",
                              null=True, blank=True)

    fax = models.CharField(max_length=255, verbose_name="Fax",
                           null=True, blank=True)

    organisation = models.ForeignKey(Organisation, related_name='people')

    def __unicode__(self):
        return u"{p.first_name} {p.family_name} <{p.email}>".format(p=self)
