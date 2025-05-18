from django.conf import settings
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/').split('?')[0]
        allowed_prefixes_for_dyzurny = [
            'dashboard/',
            'logowanie/',
            'logout/',
            'patrol/status/',
            'api/send_message/',
            'api/get_messages/',
            'messages',
        ]

        if not request.user.is_authenticated:
            # tu twoja logika dla anonimowych...
            pass

        username = getattr(request.user, 'username', '').lower()
        if username == 'dyzurny':
            if not any(path.startswith(prefix) for prefix in allowed_prefixes_for_dyzurny):
                return redirect('/dashboard/')

        return self.get_response(request)

        # Ścieżki dozwolone dla użytkownika niezalogowanego (anonimowego)
        allowed_for_anonymous = [
            'logowanie/',         # Logowanie
            'logout/',            # Wylogowanie
            'admin/login/',       # Logowanie do admina
            'dashboard/'          # Panel główny
        ]

        # Sprawdzenie, czy użytkownik jest zalogowany
        if not request.user.is_authenticated:
            # Jeśli użytkownik nie jest zalogowany i ścieżka NIE jest dozwolona, przekieruj na stronę logowania
            if path not in allowed_for_anonymous:
                return redirect(settings.LOGIN_URL)
            # Jeżeli ścieżka jest dozwolona, kontynuujemy obsługę żądania
            return self.get_response(request)

        # Dla zalogowanego użytkownika pobierz nazwę użytkownika z obiektu user
        username = getattr(request.user, 'username', '').lower()

        # Jeśli użytkownikiem jest 'dyzurny'
        if username == 'dyzurny':
            # Jeżeli obecna ścieżka NIE jest dozwolona, przekieruj na /dashboard/
            if path not in allowed_for_dyzurny:
                return redirect('/dashboard/')

        # Dla pozostałych użytkowników oraz poprawnych przypadków kontynuuj obsługę żądania
        return self.get_response(request)