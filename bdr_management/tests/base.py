import functools

from django.apps import apps
from django.db.models import Model
from django.core.urlresolvers import reverse

from django_webtest import WebTest
from webtest.forms import Select, MultipleSelect
from factory import base


class BaseWebTest(WebTest):

    csrf_checks = False

    def reverse(self, view_name, *args, **kwargs):
        return reverse(view_name, args=args, kwargs=kwargs)

    def assertObjectInDatabase(self, model, **kwargs):
        Model = self._get_model(model, kwargs)

        if Model is None:
            self.fail('Model {} does not exist'.format(model))
        try:
            return Model.objects.get(**kwargs)
        except Model.DoesNotExist:
            self.fail('Object "{}" with kwargs {} does not exist'.format(
                model, str(kwargs)
            ))

    def assertObjectNotInDatabase(self, model, **kwargs):
        Model = self._get_model(model, kwargs)
        self.assertIsNotNone(Model)
        if Model.objects.filter(**kwargs).exists():
            self.fail('Object "{}" with kwargs {} does exist'.format(
                model, str(kwargs)
            ))

    def _get_model(self, model, kwargs):
        if isinstance(model, str):
            app = kwargs.pop('app', None)
            self.assertIsNotNone(app)
            return apps.get_model(app, model)
        else:
            return model

    def get_company_form_params(self, company):
        form = company.__dict__.copy()
        for field in form:
            if form[field] is None:
                form[field] = ''
        form.update({'obligation': company.obligation.pk,
                     'country': company.country.pk})
        if company.account is not None:
            form['account'] = company.account.pk
        return form

    def get_login_for_url(self, url):
        return '%s/?next=%s' % (self.reverse('login'), url)


class mute_signals(object):
    """Temporarily disables and then restores any django signals.

        Args:
        *signals (django.dispatch.dispatcher.Signal): any django signals

        Examples:
        with mute_signals(pre_init):
        user = UserFactory.build()
        ...

        @mute_signals(pre_save, post_save)
        class UserFactory(factory.Factory):
        ...

        @mute_signals(post_save)
        def generate_users():
        UserFactory.create_batch(10)
        """

    def __init__(self, *signals):
        self.signals = signals
        self.paused = {}

    def __enter__(self):
        for signal in self.signals:
            self.paused[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, exc_type, exc_value, traceback):
        for signal, receivers in self.paused.items():
            signal.receivers = receivers
        self.paused = {}

    def __call__(self, callable_obj):
        if isinstance(callable_obj, base.FactoryMetaClass):
            # Retrieve __func__, the *actual* callable object.
            generate_method = callable_obj._generate.__func__

            @classmethod
            @functools.wraps(generate_method)
            def wrapped_generate(*args, **kwargs):
                with self:
                    return generate_method(*args, **kwargs)

            callable_obj._generate = wrapped_generate
            return callable_obj

        else:
            @functools.wraps(callable_obj)
            def wrapper(*args, **kwargs):
                with self:
                    return callable_obj(*args, **kwargs)
            return wrapper
