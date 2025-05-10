from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from Application import views
from Application.views import patrol_login_view
from Application.views import (
    wyszukaj_osobe_view,  # Widok do wyszukiwania osoby
    wyszukaj_pojazd_view,  # Widok do wyszukiwania pojazdu
    historia_view,  # Widok do wyświetlania strony historii
    logowanie_view,  # Widok do logowania
    strona_glowna_view,  # Widok do wyświetlania strony głównej
    formularz_osoba_view,  # Widok do wyświetlania formularza osoby
    szukaj_wybor_view,
    lista_osoby_pojazdy_view,
    dane_pojazd_view,
    formularz_pojazd_view,
    szukaj_osoba_pesel_view,
    szukaj_osoba_dane_view,
    notatka_view,
    rozpocznij_interwencje_view,
    dodaj_pojazd_interwencja_view
)

# Lista URL, która mapuje ścieżki URL do odpowiednich widoków
urlpatterns = [
    path('admin/', admin.site.urls),
    path('osoba/', wyszukaj_osobe_view, name='wyszukaj_osobe'),
    path('pojazd/', wyszukaj_pojazd_view, name='wyszukaj_pojazd'),
    path('dodaj_pojazd_interwencja/', dodaj_pojazd_interwencja_view, name='dodaj_pojazd_interwencja'),
    path('historia_html/', historia_view, name='historia_html'),
    path('logowanie/', views.patrol_login_view, name='patrol_login'),  # <-- NAZWA MUSI PASOWAĆ!
    path('strona_glowna_html/', strona_glowna_view, name='strona_glowna_html'),
    path('rozpocznij_interwencje/', rozpocznij_interwencje_view, name='rozpocznij_interwencje'),
    path('formularz_osoba_html/', formularz_osoba_view, name='szukaj_osoba_sposob_html'),
    path('szukaj_osoba_pesel_html/', szukaj_osoba_pesel_view, name='szukaj_osoba_pesel_html'),
    path('szukaj_osoba_dane_html/', szukaj_osoba_dane_view, name='szukaj_osoba_dane_html'),
    path('szukaj_wybor_html/', szukaj_wybor_view, name='szukaj_wybor_html'),
    path('lista_osoby_pojazdy_html/', lista_osoby_pojazdy_view, name='lista_osoby_pojazdy_html'),
    path('dane_pojazd_html/', dane_pojazd_view, name='dane_pojazd_html'),
    path('formularz_pojazd_html/', formularz_pojazd_view, name='formularz_pojazd_html'),
    path('notatka_html/', notatka_view, name='notatka_html'),

# Dodaj TĘ linię, aby obsłużyć główny adres (127.0.0.1:8000/)
    path('', strona_glowna_view, name='home'),
    path('logout/', LogoutView.as_view(next_page='/logowanie/'), name='logout'),

]

