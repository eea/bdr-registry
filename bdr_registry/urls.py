from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
import views

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),
     url(r'^organisation/add$', views.OrganisationCreate.as_view()),
     url(r'^organisation/(?P<pk>\d+)$', views.Organisation.as_view(),
            name='organisation'),
     url(r'^self_register$', views.SelfRegister.as_view()),
     url(r'^self_register/done$',
            TemplateView.as_view(template_name='self_register_done.html'),
            name='self_register_done'),
)
