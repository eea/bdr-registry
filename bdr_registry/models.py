import requests
import random
import string
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.db import models
from django.db.models.signals import pre_save

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.dispatch import receiver

from solo.models import SingletonModel
from .local import *
from django.utils.translation import ugettext_lazy as _
from post_office.models import EmailTemplate

import pyotp


def generate_key(size=20):
    crypto_random = random.SystemRandom()
    vocabulary = string.ascii_lowercase + string.digits
    return ''.join(crypto_random.choice(vocabulary) for c in range(size))


class ApiKey(models.Model):

    key = models.CharField(max_length=255, default=generate_key)
    comment = models.CharField(max_length=255)

    def __str__(self):
        return self.comment


class Country(models.Model):

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    class Meta(object):
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name


def validate_comma_separated_email_list(value):
    """
    Validate every email address in a comma separated list of emails.
    """
    value = force_text(value)

    emails = [email.strip() for email in value.split(',')]

    for email in emails:
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Invalid email: %s' % email, code='invalid')


class Obligation(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    reportek_slug = models.CharField(max_length=255)
    # TODO: update email templates
    email_template = models.ForeignKey(EmailTemplate)
    bcc = models.TextField(blank=True, validators=[validate_comma_separated_email_list])
    admins = models.ManyToManyField(User, related_name='obligations', blank=True)

    def __str__(self):
        return self.name


class AccountManager(models.Manager):

    def create_for_obligation(self, obligation, name):
        # TODO: delete this? move code in registration form
        # TODO: Check that name is available (maybe in the registration form?)
        prefix = getattr(settings, 'ACCOUNTS_PREFIX', '')
        uid = f"{prefix}{obligation.code}_{name}"
        return self.create(uid=uid)


class Account(models.Model):

    uid = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    # oauth_register is used for initial registration and reset operations.
    # It validates the TOTP token sent via email. This can bee freely changed.
    oauth_register = models.CharField(
        max_length=255, default=pyotp.random_base32())

    # oauth_secret is used for 2FA and will not be changed unless the user
    # specifically requests it from an admin.
    oauth_secret = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.uid

    objects = AccountManager()

    class Meta:
        ordering = ['uid']

    def registration_complete(self):
        # After completing the registration, an oauth_secret will be set.
        return bool(self.oauth_secret)

    def get_registration_token(self):
        totp = pyotp.TOTP(self.oauth_register, interval=86400)
        return totp.now()

    def validate_registration_token(self, token):
        return pyotp.TOTP(self.oauth_register, interval=86400).verify(token)


@receiver(pre_save, sender=Account)
def account_pre_save(sender, instance, **kwargs):
    # Ensure password is hashed.
    instance.password = (
        make_password(instance.password)
        if instance.password
        else None
    )


class Company(models.Model):

    class Meta:

        verbose_name_plural = 'Companies'

    EORI_LABEL = _('Economic Operators Registration and Identification number (EORI)')

    name = models.CharField(_('Company name'), max_length=255)
    date_registered = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    outdated = models.BooleanField(default=False)
    addr_street = models.CharField(_('Street and number'), max_length=255)
    addr_place1 = models.CharField(_('Municipality'), max_length=255)
    addr_postalcode = models.CharField(_('Postal code'), max_length=255)
    addr_place2 = models.CharField(_('Region'),
                            max_length=255, null=True, blank=True)
    eori = models.CharField(_('EORI number'), help_text=EORI_LABEL,
                            max_length=17, null=True, blank=True)
    vat_number = models.CharField(_('VAT number'), max_length=17)
    country = models.ForeignKey(Country)
    obligation = models.ForeignKey(Obligation, related_name='companies')
    website = models.URLField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('company', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def build_reporting_folder_path(self):
        # TODO: ask if using the year is ok. It used to be account.uid.
        return '/{0}/{1}/{2}'.format(
                self.obligation.reportek_slug,
                self.country.code,
                datetime.now().year)

    def has_reporting_folder(self, folder_path=None):
        if hasattr(settings, 'DISABLE_ZOPE_CONNECTION'):
            return False
        if folder_path is None:
            folder_path = self.build_reporting_folder_path()
        url = settings.BDR_API_URL + folder_path
        resp = requests.get(url, verify=False)
        if resp.status_code == 200:
            return True
        else:
            return False

    def persons_without_accounts(self):
        return self.people.filter(account__isnull=True)


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
    user = models.ForeignKey(User, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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
    account = models.OneToOneField(
        Account, null=True, blank=True, related_name='person'
    )

    @property
    def formal_name(self):
        return u"{p.title} {p.first_name} {p.family_name}".format(p=self)

    @property
    def has_account(self):
        return bool(self.account)

    def __str__(self):
        return u"{p.first_name} {p.family_name}".format(p=self)


class Comment(models.Model):
    text = models.TextField(_('Comment'))
    created = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company,
                                related_name='comments')

    def __str__(self):
        return self.created.strftime('%d %B %Y')


class ReportingYear(models.Model):

    year = models.PositiveIntegerField(unique=True)
    companies = models.ManyToManyField(Company,
                                       related_name='reporting_years',
                                       through='ReportingStatus')

    def __str__(self):
        return str(self.year)


class ReportingStatus(models.Model):

    company = models.ForeignKey(Company, related_name='reporting_statuses')
    reporting_year = models.ForeignKey(ReportingYear,
                                       related_name='reporting_statuses')
    reported = models.NullBooleanField(default=None)

    def __str__(self):
        return u"company %s reported in %s: %s" % (
            self.company.pk, self.reporting_year.year, self.reported)

    class Meta:
        unique_together = ('company', 'reporting_year',)


class SiteConfiguration(SingletonModel):

    reporting_year = models.PositiveIntegerField()
    self_register_email_template = models.ForeignKey(
        EmailTemplate,
        related_name='self_register'
    )
    register_new_account = models.ForeignKey(
        EmailTemplate, null=True, blank=True,
        related_name='register_new_account'
    )
