from django.conf import settings
from django.shortcuts import redirect

EXEMPT_URLS = [settings.LOGIN_URL.lstrip('/'), 'admin/login/']  # pozwalamy tylko na stronę logowania i admina

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/').split('?')[0]
        print('ŚCIEŻKA:', request.path_info, 'UŻYTKOWNIK:', request.user.is_authenticated)
        if not request.user.is_authenticated and path not in EXEMPT_URLS:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)