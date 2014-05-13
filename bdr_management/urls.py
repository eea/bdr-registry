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
    url(r'^companies/export/?$',
        views.CompaniesExport.as_view(),
        name='companies_export'),
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
    url(r'^companies/(?P<pk>\d+)/name-history/?$',
        views.CompanyNameHistory.as_view(),
        name='company_name_history'),

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
    url(r'^persons/export/?$',
        views.PersonsExport.as_view(),
        name='persons_export'),
    url(r'^persons/(?P<pk>\d+)/?$',
        views.PersonManagementView.as_view(),
        name='persons_view'),
    url(r'^persons/(?P<pk>\d+)/edit/?$',
        views.PersonManagementEdit.as_view(),
        name='persons_edit'),
    url(r'^persons/(?P<pk>\d+)/delete/?',
        views.PersonManagementDelete.as_view(),
        name='persons_delete'),

    url(r'^obligations/?$',
        views.Obligations.as_view(),
        name='obligations'),
    url(r'^obligations/filter/?$',
        views.ObligationsFilter.as_view(),
        name='obligations_filter'),
    url(r'^obligations/(?P<pk>\d+)/?$',
        views.ObligationView.as_view(),
        name='obligation_view'),
    url(r'^obligations/(?P<pk>\d+)/edit/?$',
        views.ObligationEdit.as_view(),
        name='obligation_edit'),
    url(r'^obligations/(?P<pk>\d+)/delete/?$',
        views.ObligationDelete.as_view(),
        name='obligation_delete'),

    url(r'^templates/?$',
        views.EmailTemplates.as_view(),
        name='email_templates'),
    url(r'^templates/add/?$',
        views.EmailTemplateCreate.as_view(),
        name='email_templates_add'),
    url(r'^templates/filter/?$',
        views.EmailTemplatesFilter.as_view(),
        name='email_templates_filter'),
    url(r'^templates/(?P<pk>\d+)/?$',
        views.EmailTemplateView.as_view(),
        name='email_template_view'),
    url(r'^templates/(?P<pk>\d+)/edit/?$',
        views.EmailTemplateEdit.as_view(),
        name='email_template_edit'),
    url(r'^templates/(?P<pk>\d+)/delete/?$',
        views.EmailTemplateDelete.as_view(),
        name='email_template_delete'),
)
