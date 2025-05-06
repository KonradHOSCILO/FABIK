from django.http import JsonResponse
from Application.firestore_fetch_data import fetch_person_by_pesel_or_data, fetch_vehicle_by_id_or_plate_or_vin
from django.shortcuts import render
from django.http import HttpResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests


# Widok odpowiedzialny za wyszukiwanie osoby na podstawie danych (pesel, imię, nazwisko, data urodzenia)
def wyszukaj_osobe_view(request):
    # Pobieramy parametry z zapytania GET
    pesel = request.GET.get("pesel")
    imie = request.GET.get("imie")
    nazwisko = request.GET.get("nazwisko")
    data_urodzenia = request.GET.get("data_urodzenia")

    # Wywołanie funkcji do pobrania osoby z bazy danych na podstawie przekazanych parametrów
    result = fetch_person_by_pesel_or_data(pesel, imie, nazwisko, data_urodzenia)

    # Jeśli wynik to odpowiedź z serwera HTTP (requests.Response)
    if isinstance(result, requests.Response):
        # Jeśli status odpowiedzi to 200, zwróć dane osoby w formacie JSON
        if result.status_code == 200:
            return JsonResponse([result.json()["fields"]], safe=False)  # Zwracamy dane jako lista
        else:
            return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)

    # Jeśli wynik to lista i zawiera dane, zwróć je również jako JSON
    elif isinstance(result, list) and result:
        return JsonResponse(result, safe=False)

    # Jeśli nie znaleziono osoby, zwróć błąd 404
    return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)


# Widok odpowiedzialny za wyszukiwanie pojazdu na podstawie identyfikatora, numeru rejestracyjnego lub VIN
def wyszukaj_pojazd_view(request):
    # Pobieramy identyfikator pojazdu z zapytania GET
    identyfikator = request.GET.get("identyfikator")

    # Wywołanie funkcji do pobrania pojazdu z bazy danych
    response, tryb = fetch_vehicle_by_id_or_plate_or_vin(identyfikator)

    # Jeśli odpowiedź jest poprawna, zwróć dane pojazdu
    if response and response.status_code == 200:
        return JsonResponse(response.json())
    else:
        # Jeśli pojazd nie został znaleziony, zwróć błąd 404
        return JsonResponse({"error": "Nie znaleziono pojazdu"}, status=404)


# Widok do wyświetlania danych osoby w formie HTML
def osoba_html_view(request):
    pesel = request.GET.get("pesel", None)
    dane = None
    # Jeśli pesel został przekazany, wyszukaj dane osoby
    if pesel:
        dane = fetch_person_by_pesel_or_data(pesel)
    # Renderowanie szablonu HTML z danymi
    return render(request, "dane_osoba_test.html", {"dane": dane})


# Widok wyświetlający stronę historii (brak logiki w tym widoku)
def historia_view(request):
    return render(request, 'historia.html')


# Widok wyświetlający stronę główną
def strona_glowna_view(request):
    return render(request, 'strona_glowna.html')


# Widok odpowiedzialny za renderowanie strony logowania
def logowanie_view(request):
    return render(request, 'logowanie.html')


# Widok wyświetlający formularz do wprowadzania danych osoby
def formularz_osoba_view(request):
    return render(request, 'formularz_osoba.html')
