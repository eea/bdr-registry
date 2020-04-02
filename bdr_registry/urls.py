from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bdr_registry import views
from bdr_management import views as management_views
from bdr_registry.views import api as api_views


admin.autodiscover()

handler500 = 'bdr_registry.views.errors.handler500'
company_patterns = [
    url(r'^add/?$',
        views.CompanyCreate.as_view()),
    url(r'^(?P<pk>\d+)/?$',
        management_views.CompaniesUpdateView.as_view(),
        name='company'),
    url(r'^(?P<pk>\d+)/update/?$',
        management_views.CompaniesUpdate.as_view(),
        name='company_update'),
    url(r'^(?P<pk>\d+)/persons/add/?$',
        management_views.PersonCreate.as_view(),
        name='person_add'),
    url(r'^(?P<pk>\d+)/comment/add/?$',
        management_views.CommentCreate.as_view(),
        name='comment_add'),
    url(r'^(?P<pk>\d+)/comment/(?P<comment_pk>\d+)/delete/?$',
        management_views.CommentDelete.as_view(),
        name='comment_delete'),
]

person_patterns = [
    url(r'^(?P<pk>\d+)/?$',
        management_views.PersonView.as_view(),
        name='person'),
    url(r'^(?P<pk>\d+)/update/?$',
        management_views.PersonEdit.as_view(),
        name='person_update'),
    url(r'^(?P<pk>\d+)/delete/?$',
        management_views.PersonDelete.as_view(),
        name='person_delete'),
]


urlpatterns = [
    url(r'^$', views.home.as_view(), name='home'),
    url(r'^accounts/login/?$', auth_views.login,
        {'template_name': 'login.html'},
        name='login'),
    url(r'^accounts/logout/?$', views.logout_view, name='logout'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^self_register/?$', views.SelfRegister.as_view(),
        name='self_register'),
    url(r'^self_register_hdv/?$', views.SelfRegisterHDV.as_view(),
        name='self_register_hpv'),
    url(r'^self_register/done/?$',
        TemplateView.as_view(template_name='self_register_done.html'),
        name='self_register_done'),
    url(r'^self_register/done/hdv/?$',
        TemplateView.as_view(template_name='self_register_done_hdv.html'),
        name='self_register_done_hdv'),
    url(r'^crashme/?$', views.crashme),
    url(r'^ping/?$', views.ping),
    url(r'^management/', include('bdr_management.urls',
                                 namespace='management')),
    url(r'^edit_company$', views.edit_company),
    url(r'^company/', include(company_patterns)),
    url(r'^person/', include(person_patterns)),
    url(r'^admin/', include(admin.site.urls)),

    # Api views
    url(r'^api/company/obligation/(?P<obligation_slug>.*)/',
        api_views.company_by_obligation),
    url(r'^organisation/all/?$', api_views.company_all),
]
urlpatterns += staticfiles_urlpatterns()
