from bdr_management.forms.utils import set_empty_label
from django.forms import BooleanField, Form, ModelForm
from bdr_registry.models import Company
from django.conf import settings


class CompanyForm(ModelForm):
    class Meta():
        model = Company
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        obligations = kwargs.pop('obligations', [])
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['obligation'].queryset = (
            self.fields['obligation'].queryset.
            filter(pk__in=obligations))

        if self.instance and self.instance.id:

            self.fields['obligation'].required = False
            self.fields['obligation'].widget.attrs['disabled'] = 'disabled'

            if not self.has_edit_permission():
                self.fields['name'].required = False
                self.fields['name'].widget.attrs['disabled'] = 'disabled'
                self.fields['account'].widget.attrs['disabled'] = 'disabled'
                self.fields['vat_number'].widget.attrs['disabled'] = 'disabled'
                self.fields['eori'].widget.attrs['disabled'] = 'disabled'
                self.fields['country'].required = False
                self.fields['country'].widget.attrs['disabled'] = 'disabled'

        set_empty_label(self.fields, '')

    def has_edit_permission(self):

        user = self.request.user
        group = settings.BDR_HELPDESK_GROUP

        if user.is_superuser or (
                    user.is_staff and
                    group in user.groups.values_list('name', flat=True)):
            return True

    def clean_name(self):
        if self.instance and self.instance.id:
            return self.instance.name
        return self.cleaned_data['name']

    def clean_obligation(self):
        if self.instance and self.instance.id:
            return self.instance.obligation
        return self.cleaned_data['obligation']

    def clean_account(self):
        if self.instance and self.instance.id:
            return self.instance.account
        return self.cleaned_data['account']

    def clean_country(self):
        if self.instance and self.instance.id and not self.has_edit_permission():
            return self.instance.country
        return self.cleaned_data['country']

    def clean_vat_number(self):
        if self.instance and self.instance.id and not self.has_edit_permission():
            return self.instance.vat_number
        return self.cleaned_data['vat_number']

    def clean_eori(self):
        if self.instance and self.instance.id and not self.has_edit_permission():
            return self.instance.eori
        return self.cleaned_data['eori']

    def clean_active(self):
        if self.instance and self.instance.id and not self.has_edit_permission():
            return self.instance.active
        return self.cleaned_data['active']

    def clean_outdated(self):
        if self.instance and self.instance.id and not self.has_edit_permission():
            return self.instance.outdated
        return self.cleaned_data['outdated']

class CompanyDeleteForm(Form):
    delete_reporting_folder = BooleanField()
    delete_account = BooleanField()
