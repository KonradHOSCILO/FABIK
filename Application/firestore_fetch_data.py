import requests
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import random, string, datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Funkcja do uzyskiwania danych uwierzytelniających z pliku JSON
def get_credentials():
    # Pobierz ścieżkę z pliku .env
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Wczytanie poświadczeń z pliku JSON
    credentials = service_account.Credentials.from_service_account_file(
        cred_path,
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    credentials.refresh(Request())
    project_id = credentials.project_id
    headers = {"Authorization": f"Bearer {credentials.token}"}
    return project_id, headers

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
def format_firestore_fields(fields):
    formatted_data = {}

    for key, value in fields.items():
        if 'stringValue' in value:
            formatted_data[key] = value['stringValue']
        elif 'integerValue' in value:
            formatted_data[key] = value['integerValue']
        elif 'arrayValue' in value:
            formatted_data[key] = [item.get('stringValue', '–') for item in value['arrayValue'].get('values', [])]
        elif 'booleanValue' in value:
            formatted_data[key] = 'Tak' if value['booleanValue'] else 'Nie'
        # Możesz dodać inne przypadki, np. dla 'mapValue', 'nullValue', itd.

    return formatted_data

def generate_random_id(length=7):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_interwencja_document():
    project_id, headers = get_credentials()
    id_interwencji = generate_random_id()
    data_today = datetime.datetime.now().strftime('%Y-%m-%d')
    document_name = f"{data_today}_{id_interwencji}_601"

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje?documentId={document_name}"

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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return document_name
    else:
        print(response.text)
        return None


def dodaj_pojazd_do_interwencji(interwencja_id, numer_rejestracyjny):
    initialize_firebase()
    db = firestore.client()
    doc_ref = db.collection('interwencje').document(interwencja_id)

    # Użyj metody arrayUnion, aby dodać numer rejestracyjny do tablicy
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
    project_id, headers = get_credentials()

    if pesel:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return format_firestore_fields(response.json().get("fields", {}))
        else:
            return None

    elif imie and nazwisko and data_urodzenia:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        all_docs = response.json().get("documents", [])
        matching = []

        for doc in all_docs:
            fields = doc.get("fields", {})
            if (
                    fields.get("imie", {}).get("stringValue", "").lower() == imie.lower() and
                    fields.get("nazwisko", {}).get("stringValue", "").lower() == nazwisko.lower() and
                    fields.get("data_urodzenia", {}).get("stringValue", "") == data_urodzenia,
            ):
                matching.append(format_firestore_fields(fields))

        return matching

# Funkcja wyszukująca pojazd po ID, numerze rejestracyjnym lub numerze VIN
def fetch_vehicle_by_plate(identyfikator):
    # Pobranie poświadczeń
    project_id, headers = get_credentials()

    # Jeśli identyfikator to numer rejestracyjny (7 znaków)
    if len(identyfikator) == 7:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{identyfikator}"
        response = requests.get(url, headers=headers)
        return response, "tablica_rejestracyjna"
    else:
        return None, "błąd"  # Błąd jeśli numer rejestracyjny nie ma odpowiedniej długości


def fetch_interwencje_by_patrol(patrol_id):
    project_id, headers = get_credentials()
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    documents = response.json().get("documents", [])
    matching = []

    for doc in documents:
        doc_id = doc.get("name", "").split("/")[-1]
        if doc_id.endswith(f"_{patrol_id}"):
            matching.append({
                "id": doc_id,
                "fields": doc.get("fields", {})
            })
    return matching

