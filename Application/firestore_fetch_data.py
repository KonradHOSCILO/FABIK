import os
import random
import string
import datetime
import requests
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from google.auth.transport.requests import Request



# Wczytujemy zmienne środowiskowe z .env, np. ścieżkę do klucza Google
load_dotenv()

_firestore_db = None  # Singleton na klienta Firestore; inicjalizujemy tylko raz

def get_firestore_db():
    """
    Inicjalizuje klienta Firestore i zwraca obiekt tego klienta.
    Używa singletonu, aby nie tworzyć wielu połączeń.
    W razie potrzeby inicjalizuje firebase_admin z pliku serwisowego.
    Zmienna środowiskowa GOOGLE_APPLICATION_CREDENTIALS MUSI być ustawiona i wskazywać na json z kontem serwisowym.
    """
    global _firestore_db
    if _firestore_db is None:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Ścieżka do pliku z kluczem serwisowym
        # firebase_admin nie pozwala na wielokrotne inicjalizacje
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _firestore_db = firestore.client()
    return _firestore_db

def get_credentials():
    """
    Pobiera poświadczenia konta serwisowego Google do bezpośredniej autoryzacji API REST.
    Zwraca project_id i nagłówki HTTP z aktualnym tokenem do autoryzacji zapytań.
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    creds = service_account.Credentials.from_service_account_file(
        cred_path,
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    # Odświeżenie tokena (konieczne do autoryzacji API)
    creds.refresh(Request())
    project_id = creds.project_id
    headers = {"Authorization": f"Bearer {creds.token}"}
    return project_id, headers

def format_firestore_fields(fields):
    """
    Przetwarza słownik pól (fields) z odpowiedzi Firestore w formacie API REST na zwykły słownik Pythona.
    Obsługuje typy: string, integer, array, boolean.
    Pozostałe typy można dodać przy potrzebie.
    """
    formatted_data = {}
    for key, value in fields.items():
        if 'stringValue' in value:
            formatted_data[key] = value['stringValue']
        elif 'integerValue' in value:
            formatted_data[key] = int(value['integerValue'])
        elif 'arrayValue' in value:
            # Każdy element tablicy to osobny słownik z typem (np. stringValue)
            formatted_data[key] = [
                item.get('stringValue', '–') for item in value['arrayValue'].get('values', [])
            ]
        elif 'booleanValue' in value:
            # Na potrzeby czytelności zwracamy "Tak"/"Nie"
            formatted_data[key] = 'Tak' if value['booleanValue'] else 'Nie'
        # Opcjonalny: obsłuż inne przypadki (mapValue, timestamp itp.)
    return formatted_data

def generate_random_id(length=7):
    """
    Generuje losowy ciąg znaków (domyślnie 7) do identyfikowania np. interwencji.
    Używa liter łacińskich i cyfr.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def fetch_patrol_status_by_username(username):
    """
    Pobiera status patrolu na podstawie jego identyfikatora (username, np. "601").
    Szuka w kolekcji 'patrole' i zwraca pole 'status' (albo None jeśli brak).
    Używa SDK Admin.
    """
    db = get_firestore_db()
    doc_ref = db.collection("patrole").document(str(username))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("status", None)
    return None

def create_interwencja_document():
    """
    Tworzy nowy dokument 'interwencja' w Firestore (kolekcja 'interwencje') z unikalnym ID i domyślnymi danymi.
    Komunikuje się przez REST API, korzysta z headera z tokenem Google.
    Zwraca wygenerowaną nazwę dokumentu lub None przy błędzie.
    """
    project_id, headers = get_credentials()
    id_interwencji = generate_random_id()
    data_today = datetime.datetime.now().strftime('%Y-%m-%d')
    # Przykład nazwy dokumentu: 2024-06-05_a8GbH8d_601
    document_name = f"{data_today}_{id_interwencji}_601"

    url = (
        f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje"
        f"?documentId={document_name}"
    )

    # Payload z gotowymi polami interwencji
    payload = {
        "fields": {
            "data_wysłania": {"stringValue": ""},
            "id_notatki": {"stringValue": id_interwencji},
            "patrol_wysylajacy": {"stringValue": "601"},
            "pesele_osob_biaracych_udzial_w_interwencji": {"arrayValue": {"values": []}},
            "pojazdy_biorace_udzial_w_interwencji": {"arrayValue": {"values": []}},
            "notatka": {"stringValue": ""},
            "status": {"stringValue": "w toku"}
        }
    }

    # Wysyłka żądania HTTP
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # Sukces: zwróć wygenerowaną nazwę dokumentu
        return document_name
    else:
        print(response.text)
        return None
def pobierz_osoby_i_pojazdy_z_interwencji(interwencja_id):
    if not interwencja_id:
        return {"error": "Brak ID interwencji"}

    project_id, headers = get_credentials()
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje/{interwencja_id}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Nie znaleziono interwencji", "status_code": response.status_code}

    document = response.json()
    fields = document.get("fields", {})

    pojazdy = []
    if "pojazdy_biorace_udzial_w_interwencji" in fields:
        pojazdy = [el["stringValue"] for el in fields["pojazdy_biorace_udzial_w_interwencji"].get("arrayValue", {}).get("values", [])]

    osoby = []
    if "pesele_osob_bioracych_udzial_w_interwencji" in fields:
        osoby = [el["stringValue"] for el in fields["pesele_osob_bioracych_udzial_w_interwencji"].get("arrayValue", {}).get("values", [])]

    return {"pojazdy": pojazdy, "osoby": osoby}

def dodaj_pojazd_do_interwencji(interwencja_id, numer_rejestracyjny=None, numer_vin=None):
    db = firestore.Client()
    pojazdy_ref = db.collection("pojazdy")
    dokumenty = pojazdy_ref.list_documents()

    pelna_nazwa = None
    logi = []

    if numer_rejestracyjny:
        for doc_ref in dokumenty:
            doc_id = doc_ref.id
            logi.append(f"Sprawdzam rejestrację: {numer_rejestracyjny} vs {doc_id}")
            if doc_id.startswith(f"{numer_rejestracyjny}_"):
                pelna_nazwa = doc_id
                break

    if not pelna_nazwa and numer_vin:
        numer_vin = numer_vin.strip().upper()
        for doc_ref in dokumenty:
            doc_id = doc_ref.id
            doc_id_upper = doc_id.strip().upper()
            logi.append(f"Sprawdzam VIN: {numer_vin} vs {doc_id_upper}")
            if doc_id_upper.endswith(f"_{numer_vin}"):
                pelna_nazwa = doc_id
                break

    if not pelna_nazwa:
        logi.append("Nie znaleziono pojazdu o podanym numerze rejestracyjnym lub VIN.")
        return False, "\n".join(logi)

    try:
        interwencja_ref = db.collection("interwencje").document(interwencja_id)
        interwencja_ref.update({
            "pojazdy_biorace_udzial_w_interwencji": firestore.ArrayUnion([pelna_nazwa])
        })
        return True, None
    except Exception as e:
        return False, f"Błąd podczas aktualizacji interwencji: {str(e)}"

def dodaj_osobe_do_interwencji(interwencja_id, pesel=None, imie=None, nazwisko=None, data_urodzenia=None):
    """
    Dodaje osobę do interwencji na podstawie PESELu lub danych osobowych.
    """
    osoba = fetch_person_by_pesel_or_data(pesel, imie, nazwisko, data_urodzenia)

    if not osoba:
        return False, "Nie znaleziono osoby"

    if isinstance(osoba, dict):
        pesel_osoby = osoba.get("pesel")
    elif isinstance(osoba, list) and len(osoba) == 1:
        pesel_osoby = osoba[0].get("pesel")
    else:
        return False, "Znaleziono wiele osób – doprecyzuj dane"

    if not pesel_osoby:
        return False, "Nie udało się ustalić PESELu"

    # Aktualizacja pola w interwencji
    project_id, headers = get_credentials()
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje/{interwencja_id}"

    payload = {
        "fields": {
            "pesele_osob_bioracych_udzial_w_interwencji": {
                "arrayValue": {
                    "values": [{"stringValue": pesel_osoby}]
                }
            }
        }
    }

    params = {
        "updateMask.fieldPaths": "pesele_osob_bioracych_udzial_w_interwencji",
        "currentDocument.exists": "true"
    }

    response = requests.patch(url, headers=headers, json=payload, params=params)

    if response.status_code not in (200, 204):
        return False, "Nie udało się dodać osoby do interwencji"

    return True, pesel_osoby




def fetch_person_by_pesel_or_data(pesel=None, imie=None, nazwisko=None, data_urodzenia=None):
    """
    Wyszukuje osobę w kolekcji 'osoby'.
    Jeśli podano pesel - szuka dokumentu po peselu (REST API).
    Jeśli nie, ale podano imie+nazwisko+data_urodzenia, przegląda całą kolekcję i filtruje wyniki po tych polach.
    Zwraca przetworzony słownik pól dla 1 osoby lub listę słowników przy drugim trybie.
    """
    project_id, headers = get_credentials()
    if pesel:
        # Tryb szukania po ID dokumentu (pesel)
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return format_firestore_fields(response.json().get("fields", {}))
        else:
            return None
    elif imie and nazwisko and data_urodzenia:
        # Tryb szukania po atrybutach osobowych
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        all_docs = response.json().get("documents", [])
        # Filtruj tylko dopasowane osoby wg przekazanych pól (ignoruj wielkość liter)
        matching = [
            format_firestore_fields(doc.get("fields", {}))
            for doc in all_docs
            if (
                doc.get("fields", {}).get("pierwsze_imie", {}).get("stringValue", "").lower() == imie.lower()
                and doc.get("fields", {}).get("nazwisko", {}).get("stringValue", "").lower() == nazwisko.lower()
                and doc.get("fields", {}).get("data_urodzenia", {}).get("stringValue", "") == data_urodzenia
            )
        ]
        return matching
    return None


def fetch_vehicle_by_plate_or_vin(identyfikator):
    """
    Szuka pojazdu w kolekcji 'pojazdy' po polu 'tablica_rejestracyjna' lub 'vin'.
    Najpierw próbuje po VIN jeśli długość to 17 znaków, w przeciwnym razie po rejestracji.
    Jeśli pierwszy nie zadziała, próbuje alternatywnie.
    """
    import requests

    project_id, headers = get_credentials()
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:runQuery"

    identyfikator = identyfikator.strip().upper()

    def run_query(field_name):
        query = {
            "structuredQuery": {
                "from": [{"collectionId": "pojazdy"}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": field_name},
                        "op": "EQUAL",
                        "value": {"stringValue": identyfikator}
                    }
                },
                "limit": 1
            }
        }
        response = requests.post(url, headers=headers, json=query)
        if response.status_code == 200:
            results = response.json()
            for result in results:
                if "document" in result:
                    return result["document"], field_name
        return None, None

    # Pierwsza próba — VIN jeśli wygląda na VIN
    if len(identyfikator) == 17:
        document, field = run_query("vin")
        if document:
            return document, field
        # Jeśli nie znaleziono, spróbuj jako tablica rejestracyjna
        return run_query("tablica_rejestracyjna")
    else:
        # Najpierw rejestracja
        document, field = run_query("tablica_rejestracyjna")
        if document:
            return document, field
        # Jeśli nie znaleziono, spróbuj jako VIN
        return run_query("vin")

    return None, "nie znaleziono"


def fetch_interwencje_by_patrol(patrol_id):
    """
    Wyszukuje wszystkie interwencje powiązane z danym patrolem.
    Pobiera wszystkie dokumenty z kolekcji 'interwencje' i wybiera te, których ID kończy się "_<patrol_id>".
    ID patrolu np. "601".
    Zwraca listę słowników: {"id": <nazwa_dokumentu>, "fields": <pola>} każdej interwencji patrolu.
    """
    project_id, headers = get_credentials()
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    documents = response.json().get("documents", [])
    matching = []
    for doc in documents:
        doc_id = doc.get("name", "").split("/")[-1]
        # Dopasowanie po suffiksie dokumentu
        if doc_id.endswith(f"_{patrol_id}"):
            matching.append({
                "id": doc_id,
                "fields": doc.get("fields", {})
            })
    return matching