from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^add/file/?$',  views.AddFile.as_view(), name='add_file'),
)
