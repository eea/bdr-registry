from django.conf.urls import patterns, url

from bdr_management.views import (Organisations, OrganisationsFilter,
                              OrganisationsManagementView, OrganisationsEdit,
                              OrganisationDelete)

from bdr_management.views import (Persons, PersonsFilter, PersonsView,
                              PersonAdd, PersonEdit, PersonDelete)

from bdr_management.views.comments import CommentCreate, CommentDelete


urlpatterns = patterns(
    '',
    url(r'^organisations$', Organisations.as_view(), name='organisations'),
    url(r'^organisations/filter$', OrganisationsFilter.as_view(),
        name='organisations_filter'),
    url(r'^organisations/(?P<pk>\d+)$', OrganisationsManagementView.as_view(),
        name='organisations_view'),

    url(r'^organisations/(?P<pk>\d+)/edit$', OrganisationsEdit.as_view(),
        name='organisations_edit'),
    url(r'^organisations/(?P<pk>\d+)/delete', OrganisationDelete.as_view(),
        name='organisations_delete'),
    url(r'^organisations/(?P<pk>\d+)/persons/add$', PersonAdd.as_view(),
        name='persons_add'),

    url(r'^organisations/(?P<pk>\d+)/comment/add', CommentCreate.as_view(),
        name='comment_add'),
    url(r'^organisations/(?P<organisation_id>\d+)/comment/(?P<pk>\d+)/delete$',
        CommentDelete.as_view(), name='comment_delete'),

    url(r'^persons$', Persons.as_view(), name='persons'),
    url(r'^persons/filter$', PersonsFilter.as_view(),
        name='persons_filter'),
    url(r'^persons/(?P<pk>\d+)$', PersonsView.as_view(),
        name='persons_view'),
    url(r'^persons/(?P<pk>\d+)/edit$', PersonEdit.as_view(),
        name='persons_edit'),
    url(r'^persons/(?P<pk>\d+)/delete', PersonDelete.as_view(),
        name='persons_delete'),

)
