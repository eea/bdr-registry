from django.forms import (
    CharField, EmailField, EmailInput, Form,
    ModelForm, ModelChoiceField, PasswordInput,
    TextInput, ValidationError
)
from bdr_registry.ldap_editor import create_ldap_editor

from bdr_registry.models import Account



class AccountForm(ModelForm):

    username =  ModelChoiceField(queryset=Account.objects.all(),
                            to_field_name='uid',
                            error_messages={'invalid_choice': 'This user does not exist in the application.'},
                            widget=TextInput())
    class Meta():
        model = Account
        fields = ()

    def clean_username(self):
        account = self.cleaned_data['username']
        if not hasattr(account, 'person'):
            raise ValidationError("The account is not a personal account.")
        return account

class PasswordResetForm(Form):
    email = EmailField(
        label="Email",
        max_length=254,
        widget=EmailInput(attrs={'autocomplete': 'email'})
    )



class SetPasswordForm(Form):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = CharField(label=("New password"),
                                    widget=PasswordInput)
    new_password2 = CharField(label=("New password confirmation"),
                                    widget=PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, account, commit=True):
        account.password = self.cleaned_data['new_password1']
        ldap_editor = create_ldap_editor()
        ldap_editor.reset_password_assert_2(account.uid, account.password)
