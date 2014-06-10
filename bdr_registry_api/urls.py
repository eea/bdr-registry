from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^notify/add/file/(?P<account>.*)/?$',
        views.notify_add_file,
        name='notify_add_file'),


)
