from django.conf.urls import patterns, url
<<<<<<< HEAD
from management.views.organisations import Organisations, OrganisationsFilter
from management.views.persons import Persons, PersonsFilter
=======
from management.views import (Organisations, OrganisationsFilter,
                              OrganisationsView)
>>>>>>> Implemented detail view for organisation


urlpatterns = patterns(
    '',
    url(r'^organisations$', Organisations.as_view(), name='organisations'),
    url(r'^organisations/filter$', OrganisationsFilter.as_view(),
        name='organisations_filter'),
    url(r'^organisations/(?P<pk>\d+)$', OrganisationsView.as_view(),
        name='organisations_view'),

    url(r'^persons$', Persons.as_view(), name='persons'),
    url(r'^persons/filter$', PersonsFilter.as_view(),
        name='persons_filter'),

)
