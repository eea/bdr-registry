from django.contrib import admin
import models


class OrganisationAdmin(admin.ModelAdmin):

    list_filter = ['country']
    list_display = ['__unicode__', 'account']


admin.site.register(models.Country)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Person)
admin.site.register(models.Obligation)
admin.site.register(models.ApiKey)
