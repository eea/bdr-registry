from django.db import models
from django.core.urlresolvers import reverse


class Country(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Obligation(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Account(models.Model):

    uid = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return u"uid={p.uid}".format(p=self)


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
                                   verbose_name="Place 2 / Region")
    country = models.ForeignKey(Country)
    obligation = models.ForeignKey(Obligation, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('organisation', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name


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
