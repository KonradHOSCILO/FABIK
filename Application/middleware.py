from django.conf import settings
from django.shortcuts import redirect

#sprawdzenie czy uzytkownik ma dostep
class LoginRequiredMiddleware:
    #przekazywanie żądania do views
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #pobiera url żądania i je formatuje
        path = request.path_info.lstrip('/').split('?')[0]

        # scieżki dozwolone dla użytkownika niezalogowanego
        allowed_for_anonymous = [
            'logowanie/',
            'logout/',
            'admin/login/',

        ]

        # Sprawdzenie czy użytkownik jest NIE zalogowany
        if not request.user.is_authenticated:
            #jeżeli nie to przekierowuje go na login
            if not any(path.startswith(prefix) for prefix in allowed_for_anonymous):
                return redirect(settings.LOGIN_URL)
            return self.get_response(request)

        # Pobranie nazwy użytkownika
        username = getattr(request.user, 'username', '').lower()

        # Dyżurny – tylko dozwolone ścieżki
        if username == 'dyzurny':
            allowed_prefixes_for_dyzurny = [
                'dashboard/',
                'historia_dyzurny/',
                'logowanie/',
                'logout/',
                'api/',
                'messages',
                'patrol/status/',
            ]

            # Jeśli to pierwsze wejście po logowaniu przekieruj na dashboard
            if path in ['', 'logowanie']:
                return redirect('/dashboard/')

            # W innym wypadku – blokuj niedozwolone
            if not any(path.startswith(prefix) for prefix in allowed_prefixes_for_dyzurny):
                return redirect('/dashboard/')

        return self.get_response(request)
