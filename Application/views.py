from django.http import JsonResponse
from Application.firestore_fetch_data import fetch_person_by_pesel_or_data, fetch_vehicle_by_id_or_plate_or_vin
from django.shortcuts import render
from django.http import HttpResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
def wyszukaj_osobe_view(request):
    pesel = request.GET.get("pesel")
    imie = request.GET.get("imie")
    nazwisko = request.GET.get("nazwisko")
    data_urodzenia = request.GET.get("data_urodzenia")

    response = fetch_person_by_pesel_or_data(pesel, imie, nazwisko, data_urodzenia)
    if response and response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)

def wyszukaj_pojazd_view(request):
    identyfikator = request.GET.get("identyfikator")
    response, tryb = fetch_vehicle_by_id_or_plate_or_vin(identyfikator)
    if response and response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Nie znaleziono pojazdu"}, status=404)

def osoba_html_view(request):
    pesel = request.GET.get("pesel", None)
    dane = None
    if pesel:
        dane = fetch_person_by_pesel_or_data(pesel)
    return render(request, "dane_osoba_test.html", {"dane": dane})

def historia_view(request):
    return render(request, 'historia.html')

def strona_glowna_view(request):
    return render(request, 'strona_glowna.html')

def logowanie_view(request):
    return render(request, 'logowanie.html')

def formularz_osoba_view(request):
    return render(request, 'formularz_osoba.html')

