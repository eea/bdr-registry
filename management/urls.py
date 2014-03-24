from django.conf.urls import patterns, url

from management.views import (Organisations, OrganisationsFilter,
                              OrganisationsView,)
from management.views import Persons, PersonsFilter, PersonsView
from management.views import Obligations, ObligationsFilter, ObligationsView


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
    url(r'^persons/(?P<pk>\d+)$', PersonsView.as_view(),
        name='persons_view'),

    url(r'^obligations$', Obligations.as_view(), name='obligations'),
    url(r'^obligations/filter$', ObligationsFilter.as_view(),
        name='obligations_filter'),
    url(r'^obligations/(?P<pk>\d+)$', ObligationsView.as_view(),
        name='obligations_view'),

)
