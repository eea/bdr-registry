from django.conf.urls import patterns, url

from management.views import (Organisations, OrganisationsFilter,
                              OrganisationsView, OrganisationsEdit)
from management.views import Persons, PersonsFilter, PersonsView


urlpatterns = patterns(
    '',
    url(r'^organisations$', Organisations.as_view(), name='organisations'),
    url(r'^organisations/filter$', OrganisationsFilter.as_view(),
        name='organisations_filter'),
    url(r'^organisations/(?P<pk>\d+)$', OrganisationsView.as_view(),
        name='organisations_view'),
    url(r'^organisations/(?P<pk>\d+)/edit$', OrganisationsEdit.as_view(),
        name='organisations_edit'),

    url(r'^persons$', Persons.as_view(), name='persons'),
    url(r'^persons/filter$', PersonsFilter.as_view(),
        name='persons_filter'),
    url(r'^persons/(?P<pk>\d+)$', PersonsView.as_view(),
        name='persons_view'),

)
