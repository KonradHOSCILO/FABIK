import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Funkcja do uzyskiwania danych uwierzytelniających z pliku JSON
def get_credentials():
    # Wczytanie poświadczeń z pliku JSON, który zawiera dane uwierzytelniające do usługi Google
    credentials = service_account.Credentials.from_service_account_file(
        'C:\\Users\\Konrad H\\Documents\\GitHub\\FABIK\\credentials.json',
        scopes=['https://www.googleapis.com/auth/datastore']  # Uprawnienia do korzystania z Datastore
    )
    # Odświeżenie tokenu dostępu
    credentials.refresh(Request())
    # Identyfikator projektu
    project_id = credentials.project_id
    # Nagłówek z tokenem autoryzacyjnym
    headers = {"Authorization": f"Bearer {credentials.token}"}
    return project_id, headers

# Funkcja wyszukująca osobę na podstawie PESEL lub danych osobowych
def fetch_person_by_pesel_or_data(pesel=None, imie=None, nazwisko=None, data_urodzenia=None):
    # Pobranie poświadczeń
    project_id, headers = get_credentials()

    # Jeśli podano PESEL, wykonaj zapytanie do Firestore, aby znaleźć osobę po PESELU
    if pesel:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
        return requests.get(url, headers=headers)

    # Jeśli podano dane osobowe, wykonaj zapytanie do Firestore, aby znaleźć osobę po imieniu, nazwisku i dacie urodzenia
    elif imie and nazwisko and data_urodzenia:
        # Zapytanie do Firestore o wszystkie dokumenty z kolekcji 'osoby'
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        # Jeśli odpowiedź jest poprawna, przeszukaj dokumenty
        all_docs = response.json().get("documents", [])
        matching = []

        for doc in all_docs:
            fields = doc.get("fields", {})
            # Sprawdzanie czy dane w dokumencie pasują do przekazanych danych
            if (
                    fields.get("imie", {}).get("stringValue", "").lower() == imie.lower() and
                    fields.get("nazwisko", {}).get("stringValue", "").lower() == nazwisko.lower() and
                    fields.get("data_urodzenia", {}).get("stringValue", "") == data_urodzenia,
            ):
                matching.append(fields)

        return matching  # Zwracamy listę pasujących osób, nie samą odpowiedź API

# Funkcja wyszukująca pojazd po ID, numerze rejestracyjnym lub numerze VIN
def fetch_vehicle_by_id_or_plate_or_vin(identyfikator):
    # Pobranie poświadczeń
    project_id, headers = get_credentials()

    # Jeśli identyfikator jest długi (to ID pojazdu), zapytanie po ID
    if "_" in identyfikator and len(identyfikator) >= 25:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{identyfikator}"
        response = requests.get(url, headers=headers)
        return response, "id"

    # Jeśli identyfikator jest numerem rejestracyjnym (7 znaków), zapytanie po numerze rejestracyjnym
    elif len(identyfikator) == 7:
        pole = "tablica_rejestracyjna"
    # Jeśli identyfikator jest numerem VIN (17 znaków), zapytanie po VIN
    elif len(identyfikator) == 17:
        pole = "vin"
    else:
        return None, "błąd"  # Błąd jeśli identyfikator nie ma odpowiedniej długości

    # Zapytanie po wszystkich dokumentach w kolekcji 'pojazdy'
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy"
    response = requests.get(url, headers=headers)
    return response, pole

