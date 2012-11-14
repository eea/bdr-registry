from django.contrib import admin
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.admin import helpers
import models


def generate_account(modeladmin, request, queryset):
    n = 0
    for organisation in queryset:
        obligation = organisation.obligation
        account = models.Account.objects.create_for_obligation(obligation)
        organisation.account = account
        organisation.save()
        n += 1
    messages.add_message(request, messages.INFO,
                         "Generated %d accounts." % n)


def reset_password(modeladmin, request, queryset):
    organisations_with_account = [o for o in queryset if o.account is not None]

    if request.POST.get('perform_reset'):
        n = 0
        for organisation in organisations_with_account:
            organisation.account.set_random_password()
            n += 1
        messages.add_message(request, messages.INFO,
                             "%d passwords have been reset." % n)
        return

    return TemplateResponse(request, 'organisation_reset_password.html', {
        'organisations_with_account': organisations_with_account,
        'queryset': queryset,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    })


class OrganisationAdmin(admin.ModelAdmin):

    list_filter = ['obligation', 'country']
    list_display = ['__unicode__', 'obligation', 'account']
    actions = [generate_account, reset_password]


admin.site.register(models.Country)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Person)
admin.site.register(models.Obligation)
admin.site.register(models.ApiKey)
