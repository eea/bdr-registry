import random
import string
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


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


class AccountManager(models.Manager):

    def create_for_obligation(self, obligation):
        rand = ''.join(str(random.randint(0, 9)) for c in range(5))
        uid = u"{o.code}{rand}".format(o=obligation, rand=rand)
        return self.create(uid=uid)


class Account(models.Model):

    uid = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return u"uid={p.uid}".format(p=self)

    def exists_in_ldap(self):
        LDAP_AUTH_BACKEND = 'django_auth_ldap.backend.LDAPBackend'
        if LDAP_AUTH_BACKEND not in settings.AUTHENTICATION_BACKENDS:
            raise RuntimeError("LDAP authentication backend is not enabled")
        from django.contrib.auth import load_backend
        from django_auth_ldap.backend import _LDAPUser
        backend = load_backend(LDAP_AUTH_BACKEND)
        ldap_user = _LDAPUser(backend, username=self.uid)
        return bool(ldap_user.dn is not None)

    def set_random_password(self):
        self.password = generate_key(size=8)
        self.save()

    objects = AccountManager()


class Organisation(models.Model):

    name = models.CharField(max_length=255,
                            verbose_name="Company name")
    date_registered = models.DateTimeField(auto_now_add=True)
    addr_street = models.CharField(max_length=255,
                                   verbose_name="Street and nr")
    addr_place1 = models.CharField(max_length=255,
                                   verbose_name="Place 1 / Municipality")
    addr_postalcode = models.CharField(max_length=255,
                                   verbose_name="Postal code")
    addr_place2 = models.CharField(max_length=255,
                                   verbose_name="Place 2 / Region",
                                   null=True, blank=True)
    country = models.ForeignKey(Country)
    obligation = models.ForeignKey(Obligation, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('organisation', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name


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
    phone = models.CharField(max_length=255, verbose_name="Telephone")
    fax = models.CharField(max_length=255, verbose_name="Fax",
                           null=True, blank=True)
    organisation = models.ForeignKey(Organisation, related_name='people')

    def __unicode__(self):
        return u"{p.first_name} {p.family_name} <{p.email}>".format(p=self)
