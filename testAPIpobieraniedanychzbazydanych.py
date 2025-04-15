import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Załaduj poświadczenia serwisowe z pliku JSON (credentials.json)
# Plik ten zawiera klucz prywatny i inne dane potrzebne do uwierzytelnienia
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/datastore']  # Ustawienie zakresu do pracy z Google Firestore
)

# Odśwież token, aby uzyskać aktualny token dostępu (Bearer Token)
credentials.refresh(Request())

# Pobierz ID projektu z poświadczeń
project_id = credentials.project_id

# Przykładowe dane do wyszukiwania w Firestore
pesel = "0111169100"  # Unikalny identyfikator osoby
rejestracja_auta = "AAPW889"  # Numer rejestracyjny pojazdu
vin_auta = "4UZ6CZE2SU9LP8R1E"  # Numer VIN pojazdu

# Zbuduj pełny URL zapytań do dokumentów w kolekcjach Firestore: "osoby" oraz "pojazdy"
urlosoby = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"
urlpojazdy = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{rejestracja_auta}_{vin_auta}"

# Przygotuj nagłówki żądania z tokenem uwierzytelniającym
headers = {
    "Authorization": f"Bearer {credentials.token}"
}

# Wykonaj zapytanie GET do dokumentu osoby (na podstawie PESEL)
responseosoby = requests.get(urlosoby, headers=headers)

# Wykonaj zapytanie GET do dokumentu pojazdu (na podstawie rejestracji i VIN)
responsepojazdy = requests.get(urlpojazdy, headers=headers)

# Obsługa odpowiedzi dla osoby
if responseosoby.status_code == 200:
    data = responseosoby.json()
    # Wyciągnij nazwisko z danych (jeśli istnieje)
    nazwisko = data['fields']['nazwisko']['stringValue']
    print("Wyszukanie zapytania API urlosoby")
    print("Surowe dane które są zwracane po wykonaniu API:", data)
    print(f"Nazwisko dla osoby o PESEL {pesel}:", nazwisko)
else:
    print(f"Błąd przy pobieraniu osoby ({responseosoby.status_code}): {responseosoby.text}")

# Obsługa odpowiedzi dla pojazdu
if responsepojazdy.status_code == 200:
    data = responsepojazdy.json()
    # Wyciągnij kolor z danych (jeśli istnieje)
    kolor = data['fields']['kolor']['stringValue']
    print("\nWyszukanie zapytania API urlpojazdy")
    print("Surowe dane które są zwracane po wykonaniu API:", data)
    print(f"Kolor auta:", kolor)
else:
    print(f"Błąd przy pobieraniu pojazdu ({responsepojazdy.status_code}): {responsepojazdy.text}")