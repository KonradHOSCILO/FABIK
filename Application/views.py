from django.http import JsonResponse
from Application.firestore_fetch_data import fetch_person_by_pesel_or_data, fetch_vehicle_by_plate, fetch_interwencje_by_patrol, create_interwencja_document, dodaj_pojazd_do_interwencji
from django.shortcuts import render, redirect
from django.http import HttpResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from Application.firestore_fetch_data import fetch_patrol_status_by_username
import requests

import json

from django.contrib.auth import authenticate, login
from django.contrib import messages

from google.cloud import firestore
from django.views.decorators.csrf import csrf_exempt

def patrol_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('strona_glowna_html')  # zmień na swój widok po zalogowaniu
        else:
            messages.error(request, "Nieprawidłowy login lub hasło.")
    return render(request, 'logowanie.html')

# [pozostałe widoki bez zmian...]

@csrf_exempt  # wyłącz na produkcji, jeśli korzystasz z Django CSRF token!
def set_patrol_status(request):
    """
    Obsługa zmiany i odczytywania statusu patrolu z Firestore po stronie serwera.
    GET - odczytuje status bieżącego patrolu (na podstawie request.user)
    POST - ustawia status bieżącego patrolu
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Brak autoryzacji"}, status=401)

    db = firestore.Client()
    username = request.user.username  # To będzie używane jako ID dokumentu patrolu

    display_map = {
        "wolny": "Wolny",
        "w_drodze": "W drodze",
        "awaria": "Awaria",
        "poza_pojazdem": "Poza pojazdem"
    }

    try:
        if request.method == "POST":
            status = request.POST.get("status")
            if not status:
                return JsonResponse({"error": "Brak statusu"}, status=400)
            doc_ref = db.collection("patrole").document(username)
            doc_ref.set({"status": status}, merge=True)
            return JsonResponse({
                "status": "ok",
                "patrol_status": status,
                "display": display_map.get(status, status)
            })

        elif request.method == "GET":
            doc_ref = db.collection("patrole").document(username)
            doc = doc_ref.get()
            if doc.exists:
                status = doc.to_dict().get("status")
            else:
                status = None
            return JsonResponse({
                "status": "ok",
                "patrol_status": status,
                "display": display_map.get(status, "brak") if status else "brak"
            })

        return JsonResponse({"error": "Metoda niedozwolona"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def wyszukaj_osobe_view(request):
    pesel = request.GET.get("pesel")
    imie = request.GET.get("imie")
    nazwisko = request.GET.get("nazwisko")
    data_urodzenia = request.GET.get("data_urodzenia")

    result = fetch_person_by_pesel_or_data(pesel, imie, nazwisko, data_urodzenia)

    if isinstance(result, dict):  # W przypadku jednej osoby
        return JsonResponse([result], safe=False)
    elif isinstance(result, list) and result:  # W przypadku wielu osób
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)


def wyszukaj_pojazd_view(request):
    identyfikator = request.GET.get("identyfikator")

    # Wywołanie funkcji do pobrania pojazdu z bazy danych
    response, tryb = fetch_vehicle_by_plate(identyfikator)

    # Jeśli odpowiedź jest poprawna, zwróć dane pojazdu
    if response and response.status_code == 200:
        return JsonResponse(response.json())
    else:
        # Jeśli pojazd nie został znaleziony, zwróć błąd 404
        return JsonResponse({"error": "Nie znaleziono pojazdu"}, status=404)

def rozpocznij_interwencje_view(request):
    if request.method == "POST":
        interwencja_id = create_interwencja_document()
        if interwencja_id:
            response = redirect("szukaj_wybor_html")
            response.set_cookie("interwencja_id", interwencja_id)
            return response
        else:
            return HttpResponse("Błąd podczas tworzenia interwencji", status=500)
    return HttpResponse("Nieprawidłowa metoda", status=405)

from django.http import JsonResponse
import json

def dodaj_pojazd_interwencja_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            interwencja_id = data.get("interwencja_id")
            numer_rejestracyjny = data.get("numer_rejestracyjny")
            numer_vin = data.get("numer_vin")

            if not interwencja_id or (not numer_rejestracyjny and not numer_vin):
                return JsonResponse({"error": "Brakuje danych"}, status=400)

            if numer_rejestracyjny:
                sukces, blad = dodaj_pojazd_do_interwencji(interwencja_id, numer_rejestracyjny)
            elif numer_vin:
                sukces, blad = dodaj_pojazd_do_interwencji(interwencja_id, numer_vin)

            if sukces:
                return JsonResponse({"status": "ok"})
            else:
                print(f"Błąd: {blad}")  # Logujemy szczegóły błędu
                return JsonResponse({"error": "Nie udało się dodać pojazdu", "details": blad}, status=500)

        except Exception as e:
            print(f"Zdarzył się błąd: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Tylko POST"}, status=405)


def historia_view(request):
    patrol_id = '601'  # Hardcodowane ID patrolu
    interwencje = fetch_interwencje_by_patrol(patrol_id)
    return render(request, 'historia.html', {'interwencje': interwencje})


# (USUNIĘTO BŁĘDNĄ DEFINICJĘ set_patrol_status TUTAJ)

def strona_glowna_view(request):
    patrol_status = None
    if request.user.is_authenticated:
        patrol_status = fetch_patrol_status_by_username(request.user.username)
    return render(request, 'strona_glowna.html', {
        'patrol_status': patrol_status,
    })

def logowanie_view(request):
    return render(request, 'logowanie.html')

def szukaj_wybor_view(request):
    return render(request, 'szukaj_wybor.html')
def szukaj_osoba_sposob_view(request):
    return render(request, 'szukaj_osoba_sposob.html')

def szukaj_osoba_pesel_view(request):
    return render(request, 'szukaj_osoba_pesel.html')

def szukaj_osoba_dane_view(request):
    return render(request, 'szukaj_osoba_dane.html')
def szukaj_pojazd_sposob_view(request):
    return render(request, 'szukaj_pojazd_sposob.html')
def szukaj_pojazd_rej_view(request):
    return render(request, 'szukaj_pojazd_rej.html')
def szukaj_pojazd_vin_view(request):
    return render(request, 'szukaj_pojazd_vin.html')
def szukaj_osoba_dane_view(request):
    return render(request, 'szukaj_osoba_dane.html')


def lista_osoby_pojazdy_view(request):
    return render(request, 'lista_osoby_pojazdy.html')

def dane_pojazd_view(request):
    return render(request, 'dane_pojazd.html')

def formularz_pojazd_view(request):
    return render(request, 'formularz_pojazd.html')

def notatka_view(request):
    return render(request, 'notatka.html')