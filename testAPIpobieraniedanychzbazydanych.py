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

# === Dane wejściowe podstawowe ===
pesel = "0111169100"
rejestracja_auta = "AV831OF"
vin_auta = "PX8E8WPSUSTE84HRR"

# === Pytania ===
def zapytaj_boolean(opis):
    odp = input(f"{opis} (tak/nie): ").strip().lower()
    return odp == "tak"

czy_badanie_techniczne = zapytaj_boolean("Czy dowód jest ważny")
czy_ubezpieczony = zapytaj_boolean("Czy pojazd jest ubezpieczony")

# === URL-e ===
urlosoby = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
urlpojazdy_base = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{rejestracja_auta}_{vin_auta}"
urlpojazdy_patch = urlpojazdy_base + "?updateMask.fieldPaths=kolor&updateMask.fieldPaths=czy_badanie_techniczne&updateMask.fieldPaths=czy_ubezpieczony"

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

backlog = []


def update_vehicle_data():
    update_data = {
        "fields": {
            "kolor": {"stringValue": "czerwony"},
            "czy_badanie_techniczne": {"booleanValue": czy_badanie_techniczne},
            "czy_ubezpieczony": {"booleanValue": czy_ubezpieczony}
        }
    }

    response = requests.patch(urlpojazdy_patch, headers=headers, json=update_data)

    if response.status_code == 200:
        print("Dane pojazdu zostały zaktualizowane.")
        backlog.append({"status": "sukces", "message": "Pojazd zaktualizowany."})
    else:
        print(f"Błąd przy aktualizacji pojazdu ({response.status_code}): {response.text}")
        backlog.append({"status": "błąd", "message": f"Błąd PATCH: {response.status_code} - {response.text}"})


# === Pobierz dane osoby ===
response_osoba = requests.get(urlosoby, headers=headers)

# === Pobierz dane pojazdu ===
response_pojazd = requests.get(urlpojazdy_base, headers=headers)

# === Obsługa osoby ===
if response_osoba.status_code == 200:
    data_osoba = response_osoba.json()
    nazwisko = data_osoba['fields'].get('nazwisko', {}).get('stringValue', 'brak')
    print(f"Nazwisko dla osoby o PESEL {pesel}: {nazwisko}")
else:
    print(f"Błąd przy pobieraniu osoby ({response_osoba.status_code}): {response_osoba.text}")
    backlog.append({"status": "błąd", "message": f"Błąd GET osoba: {response_osoba.status_code} - {response_osoba.text}"})


# === Obsługa pojazdu ===
if response_pojazd.status_code == 200:
    data_pojazd = response_pojazd.json()
    print("\nDane pojazdu:", data_pojazd)

    kolor = data_pojazd['fields'].get('kolor', {}).get('stringValue', 'nieznany')
    print(f"Aktualny kolor auta: {kolor}")

    # Aktualizacja danych
    update_vehicle_data()

    # Pobierz PESEL właściciela
    pesel_wlasciciela = data_pojazd['fields'].get('pesel_wlasciciela', {}).get('stringValue')
    if pesel_wlasciciela:
        url_wlasciciel = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel_wlasciciela}"
        response_wlasciciel = requests.get(url_wlasciciel, headers=headers)

        if response_wlasciciel.status_code == 200:
            data_wlasciciel = response_wlasciciel.json()
            punkty_karne = data_wlasciciel['fields'].get('ilosc_punktow_karnych', {}).get('integerValue', '0')
            print(f"PESEL właściciela: {pesel_wlasciciela}")
            print(f"Ilość punktów karnych: {punkty_karne}")
        else:
            print(f"Błąd przy pobieraniu właściciela ({response_wlasciciel.status_code}): {response_wlasciciel.text}")
            backlog.append({"status": "błąd", "message": f"Błąd GET właściciel: {response_wlasciciel.status_code} - {response_wlasciciel.text}"})
    else:
        print("⚠Nie znaleziono pola pesel_wlasciciela w dokumencie pojazdu.")
        backlog.append({"status": "błąd", "message": "Brak pola pesel_wlasciciela w dokumencie pojazdu."})
else:
    print(f"Błąd przy pobieraniu pojazdu ({response_pojazd.status_code}): {response_pojazd.text}")
    backlog.append({"status": "błąd", "message": f"Błąd GET pojazd: {response_pojazd.status_code} - {response_pojazd.text}"})


# === Backlog ===
print("\nBacklog:")
for log in backlog:
    print(f"{log['status'].capitalize()}: {log['message']}")
