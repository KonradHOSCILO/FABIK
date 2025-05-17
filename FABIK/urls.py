from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from Application.views import historia_interwencji, szczegoly_interwencji_api
from Application import views
from Application.views import patrol_login_view
from Application.views import (
    wyszukaj_osobe_view,
    wyszukaj_pojazd_view,
    patrol_login_view,
    strona_glowna_view,
    set_patrol_status,


    rozpocznij_interwencje_view,
    pobierz_dane_interwencji_view,
    szukaj_wybor_view,
    szukaj_osoba_sposob_view,
    szukaj_osoba_pesel_view,
    szukaj_osoba_dane_view,
    szukaj_pojazd_sposob_view,
    szukaj_pojazd_rej_view,
    szukaj_pojazd_vin_view,
    dodaj_pojazd_interwencja_view,
    dodaj_osobe_interwencja_view,
    notatka_view,
    zakoncz_interwencje_view,

    historia_view,
    lista_osoby_pojazdy_view,
    dane_pojazd_view,
    szczegoly_interwencji_api,
    szczegoly_osoby_api,
    szczegoly_pojazdu_api,
)


# Lista URL, która mapuje ścieżki URL do odpowiednich widoków
urlpatterns = [
    path('patrol/status/', set_patrol_status, name='set_patrol_status'),
    path('admin/', admin.site.urls),
    path('osoba/', wyszukaj_osobe_view, name='wyszukaj_osobe'),
    path('pojazd/', wyszukaj_pojazd_view, name='wyszukaj_pojazd'),
    path('zakoncz_notatke/', zakoncz_interwencje_view, name='zakoncz_notatke'),

    path('logowanie/', patrol_login_view, name='patrol_login'),
    path('strona_glowna_html/', strona_glowna_view, name='strona_glowna_html'),

    path('rozpocznij_interwencje/', rozpocznij_interwencje_view, name='rozpocznij_interwencje'),
    path('pobierz_dane_interwencji/', pobierz_dane_interwencji_view, name='pobierz_dane_interwencji'),
    path('szukaj_wybor_html/', szukaj_wybor_view, name='szukaj_wybor_html'),
    path('szukaj_osoba_sposob_html/', szukaj_osoba_sposob_view, name='szukaj_osoba_sposob_html'),
    path('szukaj_osoba_pesel_html/', szukaj_osoba_pesel_view, name='szukaj_osoba_pesel_html'),
    path('szukaj_osoba_dane_html/', szukaj_osoba_dane_view, name='szukaj_osoba_dane_html'),
    path('szukaj_pojazd_sposob_html/', szukaj_pojazd_sposob_view, name='szukaj_pojazd_sposob_html'),
    path('szukaj_pojazd_rej_html/', szukaj_pojazd_rej_view, name='szukaj_pojazd_rej_html'),
    path('szukaj_pojazd_vin_html/', szukaj_pojazd_vin_view, name='szukaj_pojazd_vin_html'),
    path('dodaj_pojazd_interwencja/', dodaj_pojazd_interwencja_view, name='dodaj_pojazd_interwencja'),
    path('dodaj_osobe_interwencja/', dodaj_osobe_interwencja_view, name='dodaj_osobe_interwencja'),
    path('notatka_html/', notatka_view, name='notatka_html'),


    path("historia_html/", historia_interwencji, name="historia_html"),
    path('lista_osoby_pojazdy_html/', lista_osoby_pojazdy_view, name='lista_osoby_pojazdy_html'),
    path('dane_pojazd_html/', dane_pojazd_view, name='dane_pojazd_html'),

    # Dodaj TĘ linię, aby obsłużyć główny adres (127.0.0.1:8000/)
    path('', strona_glowna_view, name='home'),
    path('logout/', LogoutView.as_view(next_page='/logowanie/'), name='logout'),

 path('historia/', historia_interwencji, name='historia'),
    path('api/interwencja/<str:interwencja_id>/', szczegoly_interwencji_api, name='szczegoly_interwencji_api'),
    path("api/interwencja/<str:interwencja_id>/", szczegoly_interwencji_api),
    path("api/osoba/<str:pesel>/", szczegoly_osoby_api),
    path("api/pojazd/<str:rejestracja>/", szczegoly_pojazdu_api),
]
