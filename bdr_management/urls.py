from django.conf.urls import patterns, url

from bdr_management import views
from django.views.generic import RedirectView


urlpatterns = patterns(
    '',

    url(r'^$', RedirectView.as_view(url='companies')),

    url(r'^companies/?$',
        views.Companies.as_view(),
        name='companies'),
    url(r'^companies/filter/?$',
        views.CompaniesFilter.as_view(),
        name='companies_filter'),
    url(r'^companies/(?P<pk>\d+)/?$',
        views.CompaniesManagementView.as_view(),
        name='companies_view'),

    url(r'^companies/add/?$',
        views.CompanyAdd.as_view(),
        name='companies_add'),
    url(r'^companies/(?P<pk>\d+)/edit/?$',
        views.CompaniesManagementEdit.as_view(),
        name='companies_edit'),
    url(r'^companies/(?P<pk>\d+)/delete/?',
        views.CompanyDelete.as_view(),
        name='companies_delete'),
    url(r'^companies/(?P<pk>\d+)/persons/add/?$',
        views.PersonManagementCreate.as_view(),
        name='persons_add'),

    url(r'^companies/(?P<pk>\d+)/comment/add/?',
        views.CommentManagementCreate.as_view(),
        name='comment_add'),
    url(r'^companies/(?P<pk>\d+)/comment/(?P<comment_pk>\d+)/delete/?',
        views.CommentManagementDelete.as_view(),
        name='comment_delete'),

    url(r'^companies/(?P<pk>\d+)/reset/password/?',
        views.ResetPassword.as_view(),
        name='reset_password'),
    url(r'^companies/(?P<pk>\d+)/create/account/?',
        views.CreateAccount.as_view(),
        name='create_account'),
    url(r'^companies/(?P<pk>\d+)/create/reporting/folder/?',
        views.CreateReportingFolder.as_view(),
        name='create_reporting_folder'),

    url(r'^persons/?$',
        views.Persons.as_view(),
        name='persons'),
    url(r'^persons/filter/?$',
        views.PersonsFilter.as_view(),
        name='persons_filter'),
    url(r'^persons/(?P<pk>\d+)/?$',
        views.PersonManagementView.as_view(),
        name='persons_view'),
    url(r'^persons/(?P<pk>\d+)/edit/?$',
        views.PersonManagementEdit.as_view(),
        name='persons_edit'),
    url(r'^persons/(?P<pk>\d+)/delete/?',
        views.PersonManagementDelete.as_view(),
        name='persons_delete'),
)
