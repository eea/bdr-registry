try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()


class ThreadLocalRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response


def get_request():
    return _thread_locals.request
