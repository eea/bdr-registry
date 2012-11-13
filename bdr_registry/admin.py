from django.contrib import admin
from django.contrib import messages
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


class OrganisationAdmin(admin.ModelAdmin):

    list_filter = ['obligation', 'country']
    list_display = ['__unicode__', 'obligation', 'account']
    actions = [generate_account]


admin.site.register(models.Country)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Person)
admin.site.register(models.Obligation)
admin.site.register(models.ApiKey)
