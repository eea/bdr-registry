from django.conf.urls import include, url
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

from bdr_management import views as management_views
from bdr_registry import views
from bdr_registry.views import api as api_views


admin.autodiscover()

company_patterns = [
    path('add/',
        views.CompanyCreate.as_view()),
    path('<int:pk>/',
        management_views.CompaniesUpdateView.as_view(),
        name='company'),
    path('<int:pk>/update/',
        management_views.CompaniesUpdate.as_view(),
        name='company_update'),
    path('<int:pk>/persons/add/',
        management_views.PersonCreate.as_view(),
        name='person_add'),
    path('<int:pk>/comment/add/',
        management_views.CommentCreate.as_view(),
        name='comment_add'),
    path('<int:pk>/comment/<int:comment_pk>/delete/',
        management_views.CommentDelete.as_view(),
        name='comment_delete'),
]

person_patterns = [
    path('<int:pk>/',
        management_views.PersonView.as_view(),
        name='person'),
    path('<int:pk>/update/',
        management_views.PersonEdit.as_view(),
        name='person_update'),
    path('<int:pk>/delete/',
        management_views.PersonDelete.as_view(),
        name='person_delete'),
]

password_set = [
    path('request/',
        management_views.PasswordSetRequest.as_view(),
        name='person_set_request'),
    path('set_new_password/<str:token>/',
        management_views.PasswordSetNewPassword.as_view(),
        name='person_set_new_password')
]

urlpatterns = [
    path('', views.home.as_view(), name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'),
        name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('captcha/', include('captcha.urls')),
    path('self_register/', views.SelfRegister.as_view(),
        name='self_register'),
    path('self_register_hdv/', views.SelfRegisterHDV.as_view(),
        name='self_register_hdv'),
    path('self_register/done/',
        TemplateView.as_view(template_name='self_register_done.html'),
        name='self_register_done'),
    path('self_register/done/hdv/',
        TemplateView.as_view(template_name='self_register_done_hdv.html'),
        name='self_register_done_hdv'),
    path('crashme/', views.crashme),
    path('ping/', views.ping),
    path('management/', include(('bdr_management.urls', 'bdr_manangement'),
                                namespace='management')),
    path('edit_company', views.edit_company),
    path('company/', include(company_patterns)),
    path('person/', include(person_patterns)),
    path("admin/", admin.site.urls),
    path('password_set/', include(password_set)),
    # Api views
    path('api/company/obligation/<slug:obligation_slug>/',
        api_views.CompanyByObligationView.as_view(),
        name='api_company_by_obligation'),
    path('organisation/all/', api_views.CompanyAllView.as_view()),
]
urlpatterns += staticfiles_urlpatterns()
