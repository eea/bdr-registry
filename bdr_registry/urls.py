from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bdr_registry import views
from bdr_management.views import OrganisationsUpdateView


admin.autodiscover()


organisation_patterns = patterns(
    '',

    url(r'^add$',
        views.OrganisationCreate.as_view()),
    url(r'^(?P<pk>\d+)$',
        OrganisationsUpdateView.as_view(),
        name='organisation'),
    url(r'^(?P<pk>\d+)/add_person$',
        views.OrganisationAddPerson.as_view(),
        name='organisation_add_person'),
    url(r'^(?P<pk>\d+)/update$',
        views.OrganisationUpdate.as_view(),
        name='organisation_update'),

)


urlpatterns = patterns(
    '',

    url(r'^$', views.home, name='home'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'},
        name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comment/(?P<pk>\d+)/delete$', views.CommentDelete.as_view(),
        name='comment_delete'),
    url(r'^comment/(?P<pk>\d+)/update$', views.CommentUpdate.as_view(),
        name='comment_update'),

    url(r'^edit_organisation$',
        views.edit_organisation),

    url(r'^person/(?P<pk>\d+)/update$', views.PersonUpdate.as_view(),
        name='person_update'),
    url(r'^person/(?P<pk>\d+)/delete$', views.PersonDelete.as_view(),
        name='person_delete'),
    url(r'^organisation/(?P<pk>\d+)/add_comment$',
        views.OrganisationAddComment.as_view(),
        name='organisation_add_comment'),
    url(r'^organisation/all$', views.organisation_all),
    url(r'^self_register$', views.SelfRegister.as_view(),
        name='self_register'),
    url(r'^self_register/done$',
        TemplateView.as_view(template_name='self_register_done.html'),
        name='self_register_done'),
    url(r'^crashme$', views.crashme),
    url(r'^ping$', views.ping),

    url(r'^management/', include('bdr_management.urls',
                                 namespace='management')),
    url(r'^organisation/', include(organisation_patterns)),
)
urlpatterns += staticfiles_urlpatterns()
