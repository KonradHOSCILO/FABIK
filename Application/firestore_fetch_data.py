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

def dodaj_pojazd_do_interwencji(interwencja_id, numer_rejestracyjny):
    """
    Dodaje numer rejestracyjny pojazdu do już istniejącej interwencji.
    Używa metody arrayUnion Firestore przez Admin SDK.
    Zapobiega duplikatom w polu-array.
    """
    db = get_firestore_db()
    doc_ref = db.collection('interwencje').document(interwencja_id)
    try:
        doc_ref.update({
            "pojazdy_biorace_udzial_w_interwencji": firestore.ArrayUnion([numer_rejestracyjny])
        })
        print("Pojazd został dodany.")
        return True, None
    except Exception as e:
        print(f"Błąd: {str(e)}")
        return False, str(e)

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
                doc.get("fields", {}).get("imie", {}).get("stringValue", "").lower() == imie.lower()
                and doc.get("fields", {}).get("nazwisko", {}).get("stringValue", "").lower() == nazwisko.lower()
                and doc.get("fields", {}).get("data_urodzenia", {}).get("stringValue", "") == data_urodzenia
            )
        ]
        return matching
    return None

def fetch_vehicle_by_plate(identyfikator):
    """
    Wyszukuje pojazd w bazie na dwa sposoby:
    1. Jeśli identyfikator ma 7 znaków - traktuje go jako numer rejestracyjny i szuka dokumentu o tej nazwie.
    2. Inaczej - zwraca błąd (obsługa VIN/ID wymagałaby osobnej logiki).
    Zwraca tuple (response, tryb_wyszukiwania).
    """
    project_id, headers = get_credentials()
    if len(identyfikator) == 7:
        # Wyszukaj pojazd po numerze rejestracyjnym
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{identyfikator}"
        response = requests.get(url, headers=headers)
        return response, "tablica_rejestracyjna"
    else:
        # Niewspierany tryb wyszukiwania w tej funkcji
        return None, "błąd"

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