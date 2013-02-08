from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse_lazy
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import views

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^$', views.home, name='home'),
     url(r'^accounts/login/$', 'django.contrib.auth.views.login',
            {'template_name': 'login.html'},
            name='login'),
     url(r'^accounts/logout/$', views.logout_view, name='logout'),
     url(r'^admin/', include(admin.site.urls)),
     url(r'^organisation/add$', views.OrganisationCreate.as_view()),
     url(r'^organisation/(?P<pk>\d+)$', views.organisation_view,
            name='organisation'),
     url(r'^edit_organisation$', views.edit_organisation),
     url(r'^organisation/(?P<pk>\d+)/update$',
            views.OrganisationUpdate.as_view(),
            name='organisation_update'),
     url(r'^organisation/(?P<pk>\d+)/add_person$',
            views.OrganisationAddPerson.as_view(),
            name='organisation_add_person'),
     url(r'^person/(?P<pk>\d+)/update$', views.PersonUpdate.as_view(),
            name='person_update'),
     url(r'^person/(?P<pk>\d+)/delete$', views.PersonDelete.as_view(),
            name='person_delete'),
     url(r'^organisation/all$', views.organisation_all),
     url(r'^self_register$', views.SelfRegister.as_view(),
            name='self_register'),
     url(r'^self_register/done$',
            TemplateView.as_view(template_name='self_register_done.html'),
            name='self_register_done'),
     url(r'^crashme$', views.crashme),
     url(r'^ping$', views.ping),
)

urlpatterns += staticfiles_urlpatterns()
