from django.db import models
from django.core.urlresolvers import reverse
from django.forms import ModelForm


class Country(models.Model):

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Organisation(models.Model):

    name = models.CharField(max_length=255,
                            verbose_name="Company name")
    addr_street = models.CharField(max_length=255,
                                   verbose_name="Street and nr")
    addr_place1 = models.CharField(max_length=255,
                                   verbose_name="Place 1 / Municipality")
    addr_postalcode = models.CharField(max_length=255,
                                   verbose_name="Postal code")
    addr_place2 = models.CharField(max_length=255,
                                   verbose_name="Place 2 / Region")
    country = models.ForeignKey(Country)

    def get_absolute_url(self):
        return reverse('organisation', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name


class SelfRegisterOrganisationForm(ModelForm):

    class Meta:
        model = Organisation


class Person(models.Model):

    title = models.CharField(max_length=255, verbose_name="Title")
    family_name = models.CharField(max_length=255, verbose_name="Family name")
    first_name = models.CharField(max_length=255, verbose_name="First name")
    email = models.EmailField(verbose_name="Email address")
    phone = models.CharField(max_length=255, verbose_name="Telephone")
    fax = models.CharField(max_length=255, verbose_name="Fax")
