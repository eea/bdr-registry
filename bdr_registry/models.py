import requests
import random
import string
from unidecode import unidecode

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from django.db import models, transaction, IntegrityError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel
from bdr_registry.ldap_editor import create_ldap_editor
from .local import *
from post_office.models import EmailTemplate


def generate_key(size=20):
    crypto_random = random.SystemRandom()
    vocabulary = string.ascii_lowercase + string.digits
    return "".join(crypto_random.choice(vocabulary) for c in range(size))


class ApiKey(models.Model):

    key = models.CharField(max_length=255, default=generate_key)
    comment = models.CharField(max_length=255)

    def __str__(self):
        return self.comment


class Country(models.Model):

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    class Meta(object):
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


def validate_comma_separated_email_list(value):
    """
    Validate every email address in a comma separated list of emails.
    """
    value = force_str(value)

    emails = [email.strip() for email in value.split(",")]

    for email in emails:
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Invalid email: %s" % email, code="invalid")


class Obligation(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    reportek_slug = models.CharField(max_length=255)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT)
    bcc = models.TextField(blank=True, validators=[validate_comma_separated_email_list])
    admins = models.ManyToManyField(User, related_name="obligations", blank=True)

    def __str__(self):
        return self.name

    @transaction.atomic
    def generate_account_id(self):
        query = NextAccountId.objects.select_for_update().filter(obligation=self)
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
        if hasattr(settings, "ACCOUNTS_PREFIX"):
            prefix = settings.ACCOUNTS_PREFIX
        else:
            prefix = ""
        uid = "{prefix}{o.code}{next_id}".format(
            prefix=prefix, o=obligation, next_id=next_id
        )
        return self.create(uid=uid)

    def create_for_person(self, company, person):
        uid = "{company}_{first_name}.{family_name}".format(
            company=company.account.uid,
            first_name=person.first_name.lower()[:3],
            family_name=person.family_name.lower()[:3],
        )
        uid = unidecode(uid)
        try:
            return self.create(uid=uid)
        except IntegrityError:
            uid = "{company}_{first_name}.{family_name}".format(
                company=company.account.uid,
                first_name=person.first_name.lower()[:4],
                family_name=person.family_name.lower()[:4],
            )
            uid = unidecode(uid)
            return self.create(uid=uid)


class Account(models.Model):

    uid = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.uid

    def set_random_password(self):
        self.password = generate_key(size=8)
        self.save()

    @property
    def exists_in_ldap(self):
        try:
            ldap_editor = create_ldap_editor()
            result = ldap_editor.search_account(self.uid)
            if result:
                return True
        except Exception as e:
            return False

    objects = AccountManager()

    @property
    def related_user(self):
        user = User.objects.filter(username=self.uid)
        if user:
            return user.first()

    class Meta:
        ordering = ["uid"]


class AccountUniqueToken(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)


class NextAccountId(models.Model):

    next_id = models.IntegerField()
    obligation = models.OneToOneField(
        Obligation, null=True, blank=True, on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return "next_id={p.next_id} ({p.obligation.name})".format(p=self)


class Company(models.Model):
    class Meta:

        verbose_name_plural = "Companies"

    EORI_LABEL = _("Economic Operators Registration and Identification number (EORI)")

    name = models.CharField(_("Company name"), max_length=255)
    date_registered = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    outdated = models.BooleanField(default=False)
    addr_street = models.CharField(_("Street and number"), max_length=255, blank=True)
    addr_place1 = models.CharField(_("Municipality"), max_length=255, blank=True)
    addr_postalcode = models.CharField(_("Postal code"), max_length=255, blank=True)
    addr_place2 = models.CharField(_("Region"), max_length=255, null=True, blank=True)
    eori = models.CharField(
        _("EORI number"), help_text=EORI_LABEL, max_length=17, null=True, blank=True
    )
    vat_number = models.CharField(_("VAT number"), max_length=17, blank=True)
    world_manufacturer_identifier = models.CharField(
        _("World Manufacturer Identifier (WMI)"), max_length=20, blank=True
    )
    linked_hdv_company = models.OneToOneField(
        "Company", null=True, blank=True, on_delete=models.PROTECT, related_name="hdv_resim_company"
    )
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.PROTECT
    )
    obligation = models.ForeignKey(
        Obligation, related_name="companies", on_delete=models.PROTECT
    )
    account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="companies",
    )
    website = models.URLField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("company", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    def build_reporting_folder_path(self):
        if self.account:
            folder_path = "/{0}/{1}/{2}".format(
                self.obligation.reportek_slug, self.country.code, self.account.uid
            )
            return folder_path
        return ""

    def has_reporting_folder(self, folder_path=None):
        if hasattr(settings, "DISABLE_ZOPE_CONNECTION"):
            return False
        if folder_path is None:
            folder_path = self.build_reporting_folder_path()
        url = settings.BDR_API_URL + folder_path
        resp = requests.get(url)
        if resp.status_code == 200:
            return True
        else:
            return False

    @property
    def main_reporter(self):
        person = self.people.filter(is_main_user=True)
        if person:
            return person.first()

    @property
    def has_main_reporter(self):
        main_user = self.people.filter(is_main_user=True)
        if main_user:
            return True

    @property
    def can_edit(self):
        if self.obligation.code == 'hdv':
            return settings.ENABLE_HDV_EDITING
        elif self.obligation.code == 'hdv_resim':
            return settings.ENABLE_HDV_RESIM_EDITING
        else:
            return True

def organisation_loaded(instance, **extra):
    instance._initial_name = "" if instance.pk is None else instance.name


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
    company = models.ForeignKey(
        Company, related_name="namehistory", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{h.name} {h.time} {h.user}".format(h=self)


class Person(models.Model):

    title = models.CharField(_("Title"), max_length=255, null=True, blank=True)
    family_name = models.CharField(_("Family name"), max_length=255)
    first_name = models.CharField(_("First name"), max_length=255)

    email = models.EmailField(_("Email address"))

    phone = models.CharField(_("Telephone"), max_length=255, blank=True)
    phone2 = models.CharField(_("Telephone 2"), max_length=255, null=True, blank=True)
    phone3 = models.CharField(_("Telephone 3"), max_length=255, null=True, blank=True)
    fax = models.CharField(_("Fax"), max_length=255, null=True, blank=True)
    account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="persons",
    )
    is_main_user = models.BooleanField(default=False)
    company = models.ForeignKey(
        Company, related_name="people", on_delete=models.CASCADE
    )

    @property
    def formal_name(self):
        title = self.title or ""
        return "{title} {p.first_name} {p.family_name}".format(title=title, p=self)

    def __str__(self):
        return "{p.first_name} {p.family_name}".format(p=self)


class Comment(models.Model):
    text = models.TextField(_("Comment"))
    created = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return self.created.strftime("%d %B %Y")


class ReportingYear(models.Model):

    year = models.PositiveIntegerField(unique=True)
    companies = models.ManyToManyField(
        Company, related_name="reporting_years", through="ReportingStatus"
    )

    def __str__(self):
        return str(self.year)


class ReportingStatus(models.Model):

    company = models.ForeignKey(
        Company, related_name="reporting_statuses", on_delete=models.CASCADE
    )
    reporting_year = models.ForeignKey(
        ReportingYear, related_name="reporting_statuses", on_delete=models.PROTECT
    )
    reported = models.BooleanField(null=True)

    def __str__(self):
        return "company %s reported in %s: %s" % (
            self.company.pk,
            self.reporting_year.year,
            self.reported,
        )

    class Meta:
        unique_together = (
            "company",
            "reporting_year",
        )


class SiteConfiguration(SingletonModel):

    reporting_year = models.PositiveIntegerField()
    self_register_email_template = models.ForeignKey(
        EmailTemplate, on_delete=models.PROTECT
    )
