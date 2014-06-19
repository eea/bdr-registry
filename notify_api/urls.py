from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^(?P<account>.*)/add/file/?$',
        views.AddFile.as_view(),
        name='add_file'),
    url(r'^(?P<account>.*)/add/feedback/?$',
        views.AddFeedback.as_view(),
        name='add_feedback'),
    url(r'^(?P<account>.*)/release/?$',
        views.Release.as_view(),
        name='release'),
)
