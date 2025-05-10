from django.contrib import admin
from django.urls import path
from Application.views import (
    wyszukaj_osobe_view,  # Widok do wyszukiwania osoby
    wyszukaj_pojazd_view,  # Widok do wyszukiwania pojazdu
    osoba_html_view,  # Widok do wyświetlania danych osoby w HTML
    historia_view,  # Widok do wyświetlania strony historii
    logowanie_view,  # Widok do logowania
    strona_glowna_view,  # Widok do wyświetlania strony głównej
    formularz_osoba_view,  # Widok do wyświetlania formularza osoby
    szukaj_wybor_view,
    lista_osoby_pojazdy_view,
    dane_pojazd_view,
    formularz_pojazd_view
)

# Lista URL, która mapuje ścieżki URL do odpowiednich widoków
urlpatterns = [
    path('admin/', admin.site.urls),
    path('osoba/', wyszukaj_osobe_view, name='wyszukaj_osobe'),
    path('pojazd/', wyszukaj_pojazd_view, name='wyszukaj_pojazd'),
    path('dane_osoba_test_html/', osoba_html_view, name='osoba_html'),
    path('historia_html/', historia_view, name='historia_html'),
    path('logowanie_html/', logowanie_view, name='logowanie_html'),
    path('strona_glowna_html/', strona_glowna_view, name='strona_glowna_html'),
    path('formularz_osoba_html/', formularz_osoba_view, name='formularz_osoba_html'),
    path('szukaj_wybor_html/', szukaj_wybor_view, name='szukaj_wybor_html'),
    path('lista_osoby_pojazdy_html/', szukaj_wybor_view, name='lista_osoby_pojazdy_html'),
    path('dane_pojazd_html/', szukaj_wybor_view, name='dane_pojazd_html'),
    path('formularz_pojazd_html/', szukaj_wybor_view, name='formularz_pojazd_html'),
]

