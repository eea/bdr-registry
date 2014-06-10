from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^notify/add/file/(?P<account>.*)/?$',
        views.notify_add_file,
        name='notify_add_file'),
    url(r'^notify/add/feedback/(?P<account>.*)/?$',
        views.notify_add_feedback,
        name='notify_add_feedback'),
    url(r'^notify/release/(?P<account>.*)/?$',
        views.notify_release,
        name='notify_release'),
)
