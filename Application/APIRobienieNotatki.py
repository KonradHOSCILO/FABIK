import requests
import random
import string
from datetime import datetime, timezone
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Autoryzacja
credentials = service_account.Credentials.from_service_account_file(
    'C:\\Users\\Konrad H\\Documents\\GitHub\\FABIK\\credentials.json',
    scopes=['https://www.googleapis.com/auth/datastore']
)
credentials.refresh(Request())

project_id = credentials.project_id
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

# === Funkcja do losowego ID notatki ===
def generate_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# === Pobierz dane od użytkownika ===
patrol = 602
notatka_opis = input("Wpisz treść notatki: ").strip()

pesele_osob = []
ile_osob = int(input("Ile osób brało udział w incydencie? ").strip())

for i in range(ile_osob):
    pesel = input(f"Podaj PESEL osoby {i+1}: ").strip()
    pesele_osob.append(pesel)

id_notatki = generate_id()
timestamp = datetime.now(timezone.utc).isoformat()

data_dokumentu = datetime.now().strftime('%Y:%m:%d_%H:%M:%S')
nazwa_dokumentu = f"{data_dokumentu}_{id_notatki}_601"

# === JSON do Firestore ===
payload = {
    "fields": {
        "id_notatki": {"stringValue": id_notatki},
        "patrol_wysylajacy": {"integerValue": int(patrol)},
        "notatka": {"stringValue": notatka_opis},
        "pesele_osob biorących udział w wydarzeniu": {
            "arrayValue": {
                "values": [{"stringValue": pesel} for pesel in pesele_osob]
            }
        },
        "data_wyslania": {"timestampValue": timestamp}
    }
}

# === Zapisz do Firestore ===
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/interwencje?documentId={nazwa_dokumentu}"
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Notatka została zapisana.")
else:
    print(f"Błąd przy zapisie notatki ({response.status_code}): {response.text}")