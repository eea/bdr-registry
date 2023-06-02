from django.urls import path
from django.views.generic import RedirectView

from bdr_management import views


urlpatterns = [
    path("", RedirectView.as_view(url="companies")),
    path("companies/", views.Companies.as_view(), name="companies"),
    path("companies/filter/", views.CompaniesFilter.as_view(), name="companies_filter"),
    path(
        "companies/delete/",
        views.CompanyDeleteMultiple.as_view(),
        name="companies_delete_multiple",
    ),
    path(
        "companies/export/excel/",
        views.CompaniesExcelExport.as_view(),
        name="companies_export",
    ),
    path(
        "companies/export/json/",
        views.CompaniesJsonExport.as_view(),
        name="companies_export_json",
    ),
    path(
        "companies/export/csv/",
        views.CompaniesCsvExport.as_view(),
        name="companies_export_csv",
    ),
    path(
        "companies/<int:pk>/",
        views.CompaniesManagementView.as_view(),
        name="companies_view",
    ),
    path(
        "companies/account/<str:account_uid>/<str:obligation_code>/",
        views.CompanyFilteredByAccountUID.as_view(),
        name="account_company",
    ),
    path(
        "username/companies/",
        views.CompaniesForUsernameView.as_view(),
        name="companies_for_username",
    ),
    path("companies/add/", views.CompanyAdd.as_view(), name="companies_add"),
    path(
        "companies/<int:pk>/edit/",
        views.CompaniesManagementEdit.as_view(),
        name="companies_edit",
    ),
    path(
        "companies/<int:pk>/delete/",
        views.CompanyDelete.as_view(),
        name="companies_delete",
    ),
    path(
        "companies/<int:pk>/persons/add/",
        views.PersonManagementCreate.as_view(),
        name="persons_add",
    ),
    path(
        "companies/<int:pk>/name-history/",
        views.CompanyNameHistory.as_view(),
        name="company_name_history",
    ),
    path(
        "companies/<int:pk>/comment/add/",
        views.CommentManagementCreate.as_view(),
        name="comment_add",
    ),
    path(
        "companies/<int:pk>/comment/<int:comment_pk>/delete/",
        views.CommentManagementDelete.as_view(),
        name="comment_delete",
    ),
    path(
        "companies/<int:pk>/reset/password/",
        views.ResetPassword.as_view(),
        name="reset_password",
    ),
    path(
        "companies/<int:pk>/reset_password_company_account/",
        views.ResetPasswordCompanyAccount.as_view(),
        name="reset_password_company_account",
    ),
    path(
        "companies/<int:pk>/set_company_account_owner/",
        views.SetCompanyAccountOwner.as_view(),
        name="set_company_account_owner",
    ),
    path(
        "companies/<int:pk>/create/account/",
        views.CreateAccount.as_view(),
        name="create_account",
    ),
    path(
        "companies/<int:pk>/create/reporting/folder/",
        views.CreateReportingFolder.as_view(),
        name="create_reporting_folder",
    ),
    path("persons/", views.Persons.as_view(), name="persons"),
    path("persons/filter/", views.PersonsFilter.as_view(), name="persons_filter"),
    path("persons/export/", views.PersonsExport.as_view(), name="persons_export"),
    path(
        "persons/export/json/",
        views.PersonsExportJson.as_view(),
        name="persons_export_json",
    ),
    path(
        "persons/<int:pk>/", views.PersonManagementView.as_view(), name="persons_view"
    ),
    path(
        "persons/<int:pk>/edit/",
        views.PersonManagementEdit.as_view(),
        name="persons_edit",
    ),
    path(
        "persons/<int:pk>/create/account/",
        views.CreateAccountPerson.as_view(),
        name="create_account_person",
    ),
    path(
        "persons/<int:pk>/disable/account/",
        views.DisableAccountPerson.as_view(),
        name="disable_account_person",
    ),
    path(
        "persons/<int:pk>/enable/account/",
        views.EnableAccountPerson.as_view(),
        name="enable_account_person",
    ),
    path(
        "persons/<int:pk>/delete/",
        views.PersonManagementDelete.as_view(),
        name="persons_delete",
    ),
    path(
        "companies/<int:cpk>/persons/<int:pk>/",
        views.PersonFromCompanyView.as_view(),
        name="person_from_company",
    ),
    path(
        "companies/<int:cpk>/persons/<int:pk>/edit/",
        views.PersonFromCompanyEdit.as_view(),
        name="person_from_company_edit",
    ),
    path(
        "companies/(<int:cpk>/persons/<int:pk>/delete/",
        views.PersonFromCompanyDelete.as_view(),
        name="person_from_company_delete",
    ),
    path("obligations/", views.Obligations.as_view(), name="obligations"),
    path("obligations/add/", views.ObligationCreate.as_view(), name="obligations_add"),
    path(
        "obligations/filter/",
        views.ObligationsFilter.as_view(),
        name="obligations_filter",
    ),
    path(
        "obligations/<int:pk>/", views.ObligationView.as_view(), name="obligation_view"
    ),
    path(
        "obligations/<int:pk>/edit/",
        views.ObligationEdit.as_view(),
        name="obligation_edit",
    ),
    path(
        "obligations/<int:pk>/delete/",
        views.ObligationDelete.as_view(),
        name="obligation_delete",
    ),
    path("templates/", views.EmailTemplates.as_view(), name="email_templates"),
    path(
        "templates/add/",
        views.EmailTemplateCreate.as_view(),
        name="email_templates_add",
    ),
    path(
        "templates/filter/",
        views.EmailTemplatesFilter.as_view(),
        name="email_templates_filter",
    ),
    path(
        "templates/<int:pk>/",
        views.EmailTemplateView.as_view(),
        name="email_template_view",
    ),
    path(
        "templates/<int:pk>/edit/",
        views.EmailTemplateEdit.as_view(),
        name="email_template_edit",
    ),
    path(
        "templates/<int:pk>/delete/",
        views.EmailTemplateDelete.as_view(),
        name="email_template_delete",
    ),
    path("settings/", views.Settings.as_view(), name="settings_view"),
    path("settings/edit/", views.SettingsEdit.as_view(), name="settings_edit"),
    path("actions/", views.Actions.as_view(), name="actions"),
    path(
        "actions/copy-report-status/",
        views.CopyReportingStatus.as_view(),
        name="copy_report_status",
    ),
]
