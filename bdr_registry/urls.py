from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),
     url(r'^organisation/add', views.OrganisationCreate.as_view()),
     url(r'^organisation/(?P<pk>\d+)', views.Organisation.as_view(),
            name='organisation'),
)
