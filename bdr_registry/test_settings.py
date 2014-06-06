
# WARNING!!
# This is a hack until there's a setting in django-assets
# to force using staticfiles finders and avoid the need
# to run collectstatics before each test run.
# see https://github.com/streema/webapp/pull/3079
# Just put this in your test settings.

from django_assets.env import DjangoResolver
use_staticfiles = property(lambda self: True)
DjangoResolver.use_staticfiles = use_staticfiles

