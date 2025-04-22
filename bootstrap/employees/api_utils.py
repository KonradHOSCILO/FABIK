# employees/api_utils.py
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Załaduj poświadczenia serwisowe
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/datastore']
)
credentials.refresh(Request())

project_id = credentials.project_id
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

def get_vehicle_data(pesel, rejestracja_auta, vin_auta):
    url_pojazd = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{rejestracja_auta}_{vin_auta}"
    response = requests.get(url_pojazd, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}