import functools

from django.db.models import Model
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

from django_webtest import WebTest
from webtest import AppError
from webtest.forms import Select, MultipleSelect
from factory import base


class BaseWebTest(WebTest):

    csrf_checks = False

    def populate_fields(self, form, data):
        for field_name, field in form.field_order:
            if field_name in data:
                value = data[field_name]
                if isinstance(value, Model):
                    value = value.pk
                if isinstance(field, MultipleSelect):
                    if not isinstance(value, list):
                        value = [value]
                if isinstance(field, (Select, MultipleSelect)):
                    field.force_value(value)
                else:
                    field.value = value
        return form

    def normalize_data(self, data):

        def convert_model_to_pk(value):
            if isinstance(value, Model):
                return value.pk
            return value

        new_data = dict(data)
        for k, v in new_data.items():
            if isinstance(v, list):
                new_data[k] = map(convert_model_to_pk, v)
            else:
                new_data[k] = convert_model_to_pk(v)
        return new_data

    def reverse(self, view_name, *args, **kwargs):
        return reverse(view_name, args=args, kwargs=kwargs)

    def assertObjectInDatabase(self, model, **kwargs):
        if isinstance(model, basestring):
            app = kwargs.pop('app', None)
            self.assertTrue(app)
            Model = get_model(app, model)
        else:
            Model = model

        if not Model:
            self.fail('Model {} does not exist'.format(model))
        try:
            return Model.objects.get(**kwargs)
        except Model.DoesNotExist:
            self.fail('Object "{}" with kwargs {} does not exist'.format(
                model, str(kwargs)
            ))

    def get_login_for_url(self, url):
        return '%s?next=%s' % (self.reverse('login'), url)


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
