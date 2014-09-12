from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bdr_registry import views
from bdr_management import views as management_views


admin.autodiscover()


company_patterns = patterns(
    '',

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
)

person_patterns = patterns(
    '',

    url(r'^(?P<pk>\d+)/?$',
        management_views.PersonView.as_view(),
        name='person'),
    url(r'^(?P<pk>\d+)/update/?$',
        management_views.PersonEdit.as_view(),
        name='person_update'),
    url(r'^(?P<pk>\d+)/delete/?$',
        management_views.PersonDelete.as_view(),
        name='person_delete'),
)


urlpatterns = patterns(
    '',

    url(r'^$', views.home, name='home'),
    url(r'^accounts/login/?$', 'django_ecas.views.login',
        name='login'),
    url(r'^accounts/logout/?$', 'django_ecas.views.logout', name='logout'),

    url(r'^self_register/?$', views.SelfRegister.as_view(),
        name='self_register'),
    url(r'^self_register/done/?$',
        TemplateView.as_view(template_name='self_register_done.html'),
        name='self_register_done'),
    url(r'^crashme/?$', views.crashme),
    url(r'^ping/?$', views.ping),

    url(r'^management/', include('bdr_management.urls',
                                 namespace='management')),
    url(r'^edit_company$', views.edit_company),
    url(r'^organisation/all/?$',
        views.company_all),
    url(r'^company/', include(company_patterns)),
    url(r'^person/', include(person_patterns)),
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()
