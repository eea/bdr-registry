from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse_lazy
import views

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^$', redirect_to, {'url': reverse_lazy('self_register')}),
     url(r'^accounts/login/$', 'django.contrib.auth.views.login',
            {'template_name': 'login.html'}),
     url(r'^admin/', include(admin.site.urls)),
     url(r'^organisation/add$', views.OrganisationCreate.as_view()),
     url(r'^organisation/(?P<pk>\d+)$', views.Organisation.as_view(),
            name='organisation'),
     url(r'^organisation/(?P<pk>\d+)/update$',
            views.OrganisationUpdate.as_view(),
            name='organisation_update'),
     url(r'^organisation/all$', views.organisation_all),
     url(r'^self_register$', views.SelfRegister.as_view(),
            name='self_register'),
     url(r'^self_register/done$',
            TemplateView.as_view(template_name='self_register_done.html'),
            name='self_register_done'),
     url(r'^crashme$', views.crashme),
)
