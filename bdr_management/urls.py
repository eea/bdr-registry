from django.conf.urls import patterns, url

from bdr_management import views


urlpatterns = patterns(
    '',

    url(r'^organisations$',
        views.Organisations.as_view(),
        name='organisations'),
    url(r'^organisations/filter$',
        views.OrganisationsFilter.as_view(),
        name='organisations_filter'),
    url(r'^organisations/(?P<pk>\d+)$',
        views.OrganisationsManagementView.as_view(),
        name='organisations_view'),

    url(r'^organisations/add$',
        views.OrganisationAdd.as_view(),
        name='organisations_add'),
    url(r'^organisations/(?P<pk>\d+)/edit$',
        views.OrganisationsManagementEdit.as_view(),
        name='organisations_edit'),
    url(r'^organisations/(?P<pk>\d+)/delete',
        views.OrganisationDelete.as_view(),
        name='organisations_delete'),
    url(r'^organisations/(?P<pk>\d+)/persons/add$',
        views.PersonAdd.as_view(),
        name='persons_add'),

    url(r'^organisations/(?P<pk>\d+)/comment/add',
        views.CommentCreate.as_view(),
        name='comment_add'),
    url(r'^organisations/(?P<organisation_id>\d+)/comment/(?P<pk>\d+)/delete$',
        views.CommentDelete.as_view(),
        name='comment_delete'),

    url(r'^persons$',
        views.Persons.as_view(),
        name='persons'),
    url(r'^persons/filter$',
        views.PersonsFilter.as_view(),
        name='persons_filter'),
    url(r'^persons/(?P<pk>\d+)$',
        views.PersonsView.as_view(),
        name='persons_view'),
    url(r'^persons/(?P<pk>\d+)/edit$',
        views.PersonEdit.as_view(),
        name='persons_edit'),
    url(r'^persons/(?P<pk>\d+)/delete',
        views.PersonDelete.as_view(),
        name='persons_delete'),
)
