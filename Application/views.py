from django.http import JsonResponse
from Application.firestore_fetch_data import fetch_person_by_pesel_or_data, fetch_vehicle_by_plate, fetch_interwencje_by_patrol, create_interwencja_document, dodaj_pojazd_do_interwencji
from django.shortcuts import render, redirect
from django.http import HttpResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests

import json

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

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




# Widok odpowiedzialny za wyszukiwanie osoby na podstawie danych (pesel, imię, nazwisko, data urodzenia)
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



# Widok odpowiedzialny za wyszukiwanie pojazdu na podstawie identyfikatora, numeru rejestracyjnego lub VIN
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

# Widok do wyświetlania danych osoby w formie HTML
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

def dodaj_pojazd_interwencja_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            interwencja_id = data.get("interwencja_id")
            numer_rejestracyjny = data.get("numer_rejestracyjny")
            if not interwencja_id or not numer_rejestracyjny:
                return JsonResponse({"error": "Brakuje danych"}, status=400)

            sukces, blad = dodaj_pojazd_do_interwencji(interwencja_id, numer_rejestracyjny)

            if sukces:
                return JsonResponse({"status": "ok"})
            else:
                print(f"Błąd: {blad}")  # Logujemy szczegóły błędu
                return JsonResponse({"error": "Nie udało się dodać pojazdu", "details": blad}, status=500)

        except Exception as e:
            print(f"Zdarzył się błąd: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Tylko POST"}, status=405)

# Widok wyświetlający stronę historii (brak logiki w tym widoku)
def historia_view(request):
    patrol_id = '601'  # Hardcodowane ID patrolu
    interwencje = fetch_interwencje_by_patrol(patrol_id)
    return render(request, 'historia.html', {'interwencje': interwencje})


# Widok wyświetlający stronę główną
def strona_glowna_view(request):
    return render(request, 'strona_glowna.html')


# Widok odpowiedzialny za renderowanie strony logowania
def logowanie_view(request):
    return render(request, 'logowanie.html')


# Widok wyświetlający formularz do wprowadzania danych osoby
def formularz_osoba_view(request):
    return render(request, 'szukaj_osoba_sposob.html')

def szukaj_osoba_pesel_view(request):
    return render(request, 'szukaj_osoba_pesel.html')

def szukaj_osoba_dane_view(request):
    return render(request, 'szukaj_osoba_dane.html')
def szukaj_wybor_view(request):
    return render(request, 'szukaj_wybor.html')

def lista_osoby_pojazdy_view(request):
    return render(request, 'lista_osoby_pojazdy.html')

def dane_pojazd_view(request):
    return render(request, 'dane_pojazd.html')

def formularz_pojazd_view(request):
    return render(request, 'formularz_pojazd.html')

def notatka_view(request):
    return render(request, 'notatka.html')