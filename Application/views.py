from django.http import JsonResponse, HttpResponse
from Application.firestore_fetch_data import (
    fetch_person_by_pesel_or_data,
    fetch_vehicle_by_plate_or_vin,
    fetch_interwencje_by_patrol,
    create_interwencja_document,
    dodaj_pojazd_do_interwencji,
    pobierz_osoby_i_pojazdy_z_interwencji,
    dodaj_osobe_do_interwencji,
    zakoncz_interwencje,
    fetch_patrol_status_by_username
)
from django.shortcuts import render, redirect
from google.cloud import firestore
from django.http import HttpResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from Application.firestore_fetch_data import fetch_patrol_status_by_username
from django.utils.timezone import make_aware, make_naive, is_aware, is_naive
import requests
import datetime

import json

from django.contrib.auth import authenticate, login
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import db

from datetime import datetime
from datetime import UTC
from google.cloud.firestore_v1 import SERVER_TIMESTAMP  # Poprawny import

from django.contrib.auth.decorators import login_required
from .models import Message
from .getmessages import pobierz_wszystkie_wiadomosci
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.timezone import make_aware, is_aware, get_default_timezone
import json





from django.contrib.auth.models import User

from django.shortcuts import redirect




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .sendmessages import wyslij_wiadomosc
from .getmessages import pobierz_wiadomosci_dla_patrolu

import json
if not firebase_admin._apps:
    cred = credentials.Certificate("./credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()


@csrf_exempt
def send_message_view(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "error": "Metoda nieobsługiwana"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "error": "Niepoprawny JSON"}, status=400)

    tresc = data.get("tresc")
    odbiorca = data.get("odbiorca")

    if not tresc or not odbiorca:
        return JsonResponse({"status": "error", "error": "Brak danych"}, status=400)

    nadawca = request.user.username if request.user.is_authenticated else "anonim"

    try:
        wyslij_wiadomosc(nadawca, odbiorca, tresc)
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=500)


def get_messages_view(request, patrol_id):
    if request.method != "GET":
        return JsonResponse({"status": "error", "error": "Metoda nieobsługiwana"}, status=405)

    try:
        print(f"get_messages_view patrol_id: {patrol_id}")
        if patrol_id == "all":
            messages = pobierz_wszystkie_wiadomosci()
        else:
            messages = pobierz_wiadomosci_dla_patrolu(patrol_id)
            messages = [msg for msg in messages if msg.get("nadawca") in ("dyzurny", patrol_id)]

        print(f"Pobrane wiadomości: {messages}")
        return JsonResponse(messages, safe=False)
    except Exception as e:
        import traceback
        print("Błąd w get_messages_view:")
        traceback.print_exc()
        return JsonResponse({"status": "error", "error": str(e)}, status=500)

# --- Widok logowania patrolu i dyżurnego ---
def patrol_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            nickname = user.username.lower()
            if nickname in [str(n) for n in range(601, 611)]:
                return redirect('/strona_glowna_html/')
            elif nickname == 'admin':
                return redirect('/admin/')
            elif nickname == 'dyzurny':
                return redirect('/dashboard/')
            else:
                return redirect('/')  # fallback na stronę główną
        else:
            messages.error(request, "Nieprawidłowy login lub hasło.")
    return render(request, 'logowanie.html')


# --- Dashboard dla dyżurnego i admina ---
@login_required
def dashboard_view(request):
    if not request.user.is_authenticated or request.user.username.lower() not in ['dyzurny', 'admin']:
        return redirect('strona_glowna_html')
    return render(request, 'dashboard.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import datetime
import json

from datetime import datetime
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def historia_dyzurny_view(request):
    if request.user.username.lower() != 'dyzurny':
        return redirect('strona_glowna_html')

    wybrany_patrol = request.GET.get('patrol', '').strip()
    interwencje_ref = db.collection('interwencje')
    dokumenty = interwencje_ref.stream()

    historia = []
    for doc in dokumenty:
        data = doc.to_dict()
        data['id_notatki'] = doc.id  # Ustawiamy klucz zgodny z JS (id_notatki, bo taki jest w JS)

        patrol = str(data.get('patrol_wysylajacy', '')).strip()
        if wybrany_patrol and patrol != wybrany_patrol:
            continue

        # Data wysłania
        data_wyslania_raw = data.get('data_wyslania') or doc.create_time
        if isinstance(data_wyslania_raw, datetime):
            dt = data_wyslania_raw
        elif isinstance(data_wyslania_raw, str):
            try:
                dt = datetime.strptime(data_wyslania_raw, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    dt = datetime.fromisoformat(data_wyslania_raw)
                except ValueError:
                    dt = None
        else:
            dt = None

        if dt:
            godzina = dt.strftime("%H:%M")
            data_str = dt.strftime("%Y-%m-%d")
            sort_key = dt
            wyswietlana_data = dt.strftime("%Y-%m-%d %H:%M")
        else:
            godzina = "??:??"
            data_str = "brak_daty"
            sort_key = datetime.min
            wyswietlana_data = "brak"

        nazwa = f"{patrol} {godzina} {data_str} {doc.id}"
        data['nazwa_interwencji'] = nazwa
        data['data_wyslania'] = wyswietlana_data
        data['_sort_key'] = sort_key

        historia.append(data)

    historia.sort(key=lambda x: x['_sort_key'], reverse=True)
    for item in historia:
        item.pop('_sort_key', None)

    patrole = [str(num) for num in range(601, 611)]
    historia_json = json.dumps(historia)

    return render(request, 'historia_dyzurny.html', {
        'historia': historia,  # <--- dodajemy pełną listę interwencji
        'historia_json': historia_json,
        'patrole': patrole,
        'user_id': request.user.username.lower(),
        'wybrany_patrol': wybrany_patrol,
    })






@csrf_exempt
def set_patrol_status(request):
    """Obsługuje zmianę lub pobieranie statusu patrolu w Firestore"""
    print(f"\n=== Rozpoczęto przetwarzanie żądania ===")
    print(f"Metoda: {request.method}")
    print(f"Użytkownik: {request.user}")
    print(f"Nagłówki: {dict(request.headers)}")
    print(f"Dane POST: {request.POST}")
    print(f"Zawartość ciała: {request.body.decode()}")

    if not request.user.is_authenticated:
        print("=== BRAK AUTORYZACJI ===")
        return JsonResponse({"error": "Brak autoryzacji"}, status=401)

    try:
        db = firestore.Client()
    except Exception as e:
        print(f"Błąd Firestore: {str(e)}")
        return JsonResponse({"error": "Błąd połączenia z bazą"}, status=500)

    username = request.user.username.lower()
    is_dyzurny = (username == "dyzurny")

    display_map = {
        "wolny": "Wolny",
        "w_drodze": "W drodze",
        "awaria": "Awaria",
        "poza_pojazdem": "Poza pojazdem",
        "na_interwencji": "Na interwencji"
    }

    try:
        if request.method == "POST":
            print("\n=== PRZETWARZANIE POST ===")

            if is_dyzurny:
                data = json.loads(request.body.decode("utf-8"))
                patrol_number = data.get("patrol_number")
                new_status = data.get("new_status")
                print(f"Dyżurny zmienia patrol {patrol_number} na {new_status}")
                if not patrol_number or not new_status:
                    return JsonResponse({"error": "Brak danych"}, status=400)
            else:
                data = json.loads(request.body.decode("utf-8"))
                new_status = data.get("new_status")
                print(f"Patrol {username} próbuje ustawić status: {new_status}")
                patrol_number = username
                if not new_status:
                    return JsonResponse({"error": "Brak statusu"}, status=400)

            doc_ref = db.collection("patrole").document(str(patrol_number))
            doc_ref.set({
                "status": new_status,
                "kryptonim": str(patrol_number),
                "last_updated": SERVER_TIMESTAMP
            }, merge=True)
            print("Zapisano w Firestore!")

            return JsonResponse({
                "status": "ok",
                "message": f"Status zmieniono na: {display_map.get(new_status, new_status)}",
                "display": display_map.get(new_status, new_status)
            })

        elif request.method == "GET":
            print("\n=== PRZETWARZANIE GET ===")

            if is_dyzurny:
                patrol_number = request.GET.get("patrol_number")
                if not patrol_number:
                    return JsonResponse({"error": "Brak numeru patrolu"}, status=400)
            else:
                patrol_number = username

            doc_ref = db.collection("patrole").document(str(patrol_number))
            doc = doc_ref.get()

            if doc.exists:
                status_data = doc.to_dict()
                fs_timestamp = status_data.get("last_updated")
                iso_timestamp = fs_timestamp.isoformat().replace("+00:00", "Z") if fs_timestamp else None

                return JsonResponse({
                    "status": "ok",
                    "display": display_map.get(status_data.get("status"), "brak statusu"),
                    "timestamp": iso_timestamp
                })
            else:
                return JsonResponse({
                    "status": "ok",
                    "display": "brak statusu",
                    "timestamp": None
                })

        else:
            return JsonResponse({"error": "Metoda niedozwolona"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Nieprawidłowy format danych"}, status=400)
    except Exception as e:
        print(f"\n=== BŁĄD: {str(e)} ===")
        return JsonResponse({"error": str(e)}, status=500)


def rozpocznij_interwencje_view(request):
    if request.method == "POST":
        numer_patrolu = request.user.username
        interwencja_id = create_interwencja_document(numer_patrolu)
        if interwencja_id:
            response = redirect("szukaj_wybor_html")
            response.set_cookie("interwencja_id", interwencja_id)
            return response
        else:
            return HttpResponse("Błąd podczas tworzenia interwencji", status=500)
    return HttpResponse("Nieprawidłowa metoda", status=405)

def pobierz_dane_interwencji_view(request):
    interwencja_id = request.GET.get("id")
    dane = pobierz_osoby_i_pojazdy_z_interwencji(interwencja_id)
    if "error" in dane:
        return JsonResponse({"error": dane["error"]}, status=dane.get("status_code", 400))
    return JsonResponse(dane)

def wyszukaj_osobe_view(request):
    pesel = request.GET.get("pesel")
    imie = request.GET.get("imie")
    nazwisko = request.GET.get("nazwisko")
    data_urodzenia = request.GET.get("data_urodzenia")
    result = fetch_person_by_pesel_or_data(pesel, imie, nazwisko, data_urodzenia)
    if isinstance(result, dict):  # jedna osoba
        return JsonResponse([result], safe=False)
    elif isinstance(result, list) and result:
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)

def wyszukaj_pojazd_view(request):
    identyfikator = request.GET.get("identyfikator")
    document, tryb = fetch_vehicle_by_plate_or_vin(identyfikator)
    if document:
        return JsonResponse(document)
    else:
        return JsonResponse({"error": "Nie znaleziono pojazdu"}, status=404)

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
                sukces, blad = dodaj_pojazd_do_interwencji(
                    interwencja_id=interwencja_id,
                    numer_rejestracyjny=numer_rejestracyjny,
                )
            elif numer_vin:
                sukces, blad = dodaj_pojazd_do_interwencji(
                    interwencja_id=interwencja_id,
                    numer_vin=numer_vin,
                )

            if sukces:
                return JsonResponse({"status": "ok"})
            else:
                print(f"Błąd: {blad}")
                return JsonResponse({"error": "Nie udało się dodać pojazdu", "details": blad}, status=500)
        except Exception as e:
            print(f"Zdarzył się błąd: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Tylko POST"}, status=405)

def dodaj_osobe_interwencja_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            interwencja_id = data.get("interwencja_id")
            pesel = data.get("pesel")
            imie = data.get("imie")
            nazwisko = data.get("nazwisko")
            data_urodzenia = data.get("data_urodzenia")

            if not interwencja_id or (not pesel and not (imie and nazwisko and data_urodzenia)):
                return JsonResponse({"error": "Brakuje danych"}, status=400)

            sukces, blad = dodaj_osobe_do_interwencji(
                interwencja_id=interwencja_id,
                pesel=pesel,
                imie=imie,
                nazwisko=nazwisko,
                data_urodzenia=data_urodzenia
            )

            if sukces:
                return JsonResponse({"status": "ok"})
            else:
                return JsonResponse({"error": "Nie udało się dodać osoby do interwencji", "details": blad}, status=500)
        except Exception as e:
            print(f"Zdarzył się błąd: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Tylko POST"}, status=405)

def zakoncz_interwencje_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            interwencja_id = data.get("interwencja_id")
            notatka = data.get("notatka")

            if not interwencja_id or not notatka:
                return JsonResponse({"error": "Brakuje danych"}, status=400)

            sukces, blad = zakoncz_interwencje(
                interwencja_id=interwencja_id,
                notatka=notatka,
            )

            if sukces:
                response = JsonResponse({"status": "ok"})
                response.delete_cookie("interwencja_id")
                return response
            else:
                return JsonResponse({"error": "Nie udało się zakończyć interwencji", "details": blad}, status=500)
        except Exception as e:
            print(f"Zdarzył się błąd: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Tylko POST"}, status=405)


def historia_view(request):
    # Dla uproszczenia przykładowo hardkodowany patrol_id
    patrol_id = '601'
    interwencje = fetch_interwencje_by_patrol(patrol_id)
    return render(request, 'historia_html.html', {'interwencje': interwencje})

def strona_glowna_view(request):
    patrol_status = None
    username = ""
    interwencje_count = 0

    if request.user.is_authenticated:
        username = request.user.username
        patrol_status = fetch_patrol_status_by_username(username)

        if patrol_status:
            db = firestore.client()
            all_docs = db.collection("interwencje").stream()

            # Liczymy tylko te, których ID kończy się na _{username}
            interwencje_count = sum(1 for doc in all_docs if doc.id.startswith(datetime.today().strftime("%Y-%m-%d")) and doc.id.endswith(f"_{username}"))

    return render(request, 'strona_glowna.html', {
        'patrol_status': patrol_status,
        'username': username,
        'interwencje_count': interwencje_count,
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

def notatka_view(request):
    return render(request, 'notatka.html')

def lista_osoby_pojazdy_view(request):
    return render(request, 'lista_osoby_pojazdy.html')

def dane_pojazd_view(request):
    return render(request, 'dane_pojazd.html')

def formularz_pojazd_view(request):
    return render(request, 'formularz_pojazd.html')

def notatka_view(request):
    return render(request, 'notatka.html')

# Inicjalizacja Firebase (tylko raz)
if not firebase_admin._apps:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)

# Widok: historia interwencji
def historia_interwencji(request):
    db = firestore.client()
    historia = []

    user_id = str(request.user.username)
    wybrany_patrol = request.GET.get("patrol")

    # Dobierz odpowiednie zapytanie w zależności od użytkownika
    if user_id == "dyzurny":
        if wybrany_patrol:
            query = db.collection("interwencje").where("patrol_wysylajacy", "==", wybrany_patrol)
        else:
            query = db.collection("interwencje")
    else:
        query = db.collection("interwencje").where("patrol_wysylajacy", "==", user_id)

    # Pobierz wszystkie interwencje z zapytania
    wszystkie = query.stream()

    # Filtrowanie i sortowanie po stronie Pythona
    interwencje_z_data = []
    for doc in wszystkie:
        dane = doc.to_dict()
        data_rozp = dane.get("data_rozpoczęcia")
        if data_rozp:  # pomijaj jeśli brak daty rozpoczęcia
            interwencje_z_data.append((doc.id, data_rozp))

    # Sortowanie malejąco (najnowsze najpierw)
    interwencje_z_data.sort(key=lambda x: x[1], reverse=True)

    for doc_id, data_rozp in interwencje_z_data:
        historia.append({
            "id": doc_id,
            "czas": data_rozp
        })

    lista_patroli = ["601", "602", "603", "admin", "dyzurny"]

    return render(request, "historia_html.html", {
        "historia": historia,
        "user_id": user_id,
        "lista_patroli": lista_patroli,
        "wybrany_patrol": wybrany_patrol
    })

    # Przykładowa lista dostępnych patroli — możesz to dynamicznie generować z bazy
    lista_patroli = ["601", "602", "603", "admin", "dyzurny"]

    return render(request, "historia_html.html", {
        "historia": historia,
        "user_id": user_id,
        "lista_patroli": lista_patroli,
        "wybrany_patrol": wybrany_patrol
    })

# Widok: szczegóły jednej interwencji
def szczegoly_interwencji_api(request, interwencja_id):
    db = firestore.client()
    doc = db.collection("interwencje").document(interwencja_id).get()
    if doc.exists:
        dane = doc.to_dict()
        return JsonResponse({
            "notatka": dane.get("notatka", ""),
            "status": dane.get("status", ""),
            "pesele": dane.get("pesele_osob_bioracych_udzial_w_interwencji", []),
            "pojazdy": dane.get("pojazdy_biorace_udzial_w_interwencji", [])
        })
    return JsonResponse({"error": "Nie znaleziono"}, status=404)

def szczegoly_osoby_api(request, pesel):
    db = firestore.client()
    doc = db.collection("osoby").document(pesel).get()
    if doc.exists:
        return JsonResponse(doc.to_dict())
    return JsonResponse({"error": "Nie znaleziono osoby"}, status=404)

def szczegoly_pojazdu_api(request, rejestracja):
    db = firestore.client()
    doc = db.collection("pojazdy").document(rejestracja).get()
    if doc.exists:
        return JsonResponse(doc.to_dict())
    return JsonResponse({"error": "Nie znaleziono pojazdu"}, status=404)
