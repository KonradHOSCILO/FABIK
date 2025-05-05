"""
URL configuration for FABIK project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Application.views import (
    wyszukaj_osobe_view,
    wyszukaj_pojazd_view,
    osoba_html_view,
    historia_view,
    logowanie_view,
    strona_glowna_view,
    formularz_osoba_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('osoba/', wyszukaj_osobe_view, name='wyszukaj_osobe'),
    path('pojazd/', wyszukaj_pojazd_view, name='wyszukaj_pojazd'),
    path('dane_osoba_test_html/', osoba_html_view, name='osoba_html'),
    path('historia_html/', historia_view, name='historia_html'),
    path('logowanie_html/', logowanie_view, name='logowanie_html'),
    path('strona_glowna_html/', strona_glowna_view, name='strona_glowna_html'),
    path('formularz_osoba_html/', formularz_osoba_view, name='formularz_osoba_html'),
]

