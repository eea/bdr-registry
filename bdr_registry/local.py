try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()


class ThreadLocalRequestMiddleware(object):

    def process_request(self, request):
        _thread_locals.request = request


def get_request():
    return _thread_locals.request
