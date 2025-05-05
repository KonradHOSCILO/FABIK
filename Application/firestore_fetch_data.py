import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        'C:\\Users\\Konrad H\\Documents\\GitHub\\FABIK\\credentials.json',
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    credentials.refresh(Request())
    project_id = credentials.project_id
    headers = {"Authorization": f"Bearer {credentials.token}"}
    return project_id, headers

def fetch_person_by_pesel_or_data(pesel=None, imie=None, nazwisko=None, data_urodzenia=None):
    project_id, headers = get_credentials()

    if pesel:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
        response = requests.get(url, headers=headers)
        return response

    elif imie and nazwisko and data_urodzenia:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby"
        response = requests.get(url, headers=headers)
        return response

    return None

def fetch_vehicle_by_id_or_plate_or_vin(identyfikator):
    project_id, headers = get_credentials()

    if "_" in identyfikator and len(identyfikator) >= 25:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{identyfikator}"
        response = requests.get(url, headers=headers)
        return response, "id"

    elif len(identyfikator) == 7:
        pole = "tablica_rejestracyjna"
    elif len(identyfikator) == 17:
        pole = "vin"
    else:
        return None, "błąd"

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy"
    response = requests.get(url, headers=headers)
    return response, pole