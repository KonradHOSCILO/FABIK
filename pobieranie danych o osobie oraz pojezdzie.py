import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def wyswietl_dane_osoby():
    # Ładowanie danych uwierzytelniających z pliku JSON
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json',  # Ścieżka do pliku z danymi uwierzytelniającymi
        scopes=['https://www.googleapis.com/auth/datastore']  # Zakresy dostępu do bazy danych
    )
    credentials.refresh(Request())  # Odświeżenie tokena uwierzytelniającego
    project_id = credentials.project_id  # ID projektu w Google Cloud
    headers = {"Authorization": f"Bearer {credentials.token}"}  # Nagłówek z tokenem uwierzytelniającym

    # Zapytanie o sposób wyszukiwania
    wybor = input("Czy chcesz wyszukać po PESEL (1), czy po imieniu, nazwisku i dacie urodzenia (2)? Wpisz 1 lub 2: ")

    if wybor == "1":
        # Wyszukiwanie po PESEL
        pesel = input("Podaj PESEL: ").strip()  # Usuwanie zbędnych spacji
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby/{pesel}"  # Tworzenie URL do wyszukiwania
        response = requests.get(url, headers=headers)  # Wykonanie zapytania do Firestore

        if response.status_code == 200:
            pola = response.json().get("fields", {})  # Odczyt danych osoby z odpowiedzi
        else:
            print(f"Nie znaleziono osoby o PESELu: {pesel}")
            return  # Zakończenie funkcji, jeśli nie znaleziono

    elif wybor == "2":
        # Wyszukiwanie po imieniu, nazwisku i dacie urodzenia
        imie = input("Podaj imię: ").strip().lower()
        nazwisko = input("Podaj nazwisko: ").strip().lower()
        data_urodzenia = input("Podaj datę urodzenia (rrrr-mm-dd): ").strip()

        # Szukanie po wszystkich osobach
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/osoby"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Błąd podczas pobierania danych.")
            return  # Zakończenie funkcji, jeśli wystąpił błąd podczas pobierania danych

        znaleziony = False  # Flaga informująca o znalezieniu osoby
        for dokument in response.json().get('documents', []):
            pola = dokument.get('fields', {})

            imie_doc = pola.get("pierwsze_imie", {}).get("stringValue", "").lower()
            nazwisko_doc = pola.get("nazwisko", {}).get("stringValue", "").lower()
            data_doc = pola.get("data_urodzenia", {}).get("stringValue", "")

            # Porównanie danych
            if imie == imie_doc and nazwisko == nazwisko_doc and data_urodzenia == data_doc:
                znaleziony = True
                break

        if not znaleziony:
            print("Nie znaleziono osoby o podanych danych.")
            return

    else:
        print("Nieprawidłowa opcja.")
        return

    # Wyświetlanie danych osoby
    dane = {}
    for key, value in pola.items():
        if 'arrayValue' in value:
            lista = value['arrayValue'].get('values', [])
            dane[key] = [el['stringValue'] for el in lista]  # Jeśli jest lista, dodajemy jej elementy
        else:
            for value_type in value:
                dane[key] = value[value_type]  # Przypisanie wartości

    # Wyświetlanie danych w czytelnej formie
    print("\nDANE OSOBY:")
    for k, v in dane.items():
        if isinstance(v, list):
            print(f"{k}: {', '.join(v)}")
        else:
            print(f"{k}: {v}")
    print("-" * 40)

def wyswietl_dane_pojazdu():
    # Ładowanie danych uwierzytelniających z pliku JSON
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    credentials.refresh(Request())
    project_id = credentials.project_id
    headers = {"Authorization": f"Bearer {credentials.token}"}  # Nagłówek z tokenem uwierzytelniającym

    # Zapytanie o numer rejestracyjny lub VIN
    identyfikator = input("Podaj tablicę rejestracyjną, numer VIN lub pełny identyfikator dokumentu: ").strip().upper()

    # Jeśli użytkownik podał pełny identyfikator dokumentu
    if "_" in identyfikator and len(identyfikator) >= 25:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy/{identyfikator}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Nie znaleziono pojazdu o identyfikatorze {identyfikator}.")
            return

        fields = response.json().get("fields", {})
        dane = {}
        for key, value in fields.items():
            if 'arrayValue' in value:
                lista = value['arrayValue'].get('values', [])
                dane[key] = [el.get('stringValue', '') for el in lista]
            else:
                for value_type in value:
                    dane[key] = value[value_type]

        print(f"\nDANE POJAZDU (ID = {identyfikator}):")
        for k, v in dane.items():
            if isinstance(v, list):
                print(f"{k}: {', '.join(v)}")
            else:
                print(f"{k}: {v}")
        print("-" * 40)
        return

    # Inaczej sprawdzamy długość i szukamy po tablicy lub VINie
    if len(identyfikator) == 7:
        pole = "tablica_rejestracyjna"
    elif len(identyfikator) == 17:
        pole = "vin"
    else:
        print("Nieprawidłowy numer rejestracyjny lub VIN.\nTablica rejestracyjna powinna mieć 7 znaków, a VIN 17.")
        return

    # Przeszukiwanie całej kolekcji
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/pojazdy"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Błąd podczas pobierania danych z bazy.")
        return

    documents = response.json().get("documents", [])
    znaleziono = False

    # Szukanie pojazdu w kolekcji
    for doc in documents:
        fields = doc.get("fields", {})
        wartosc = fields.get(pole, {}).get("stringValue", "")
        if wartosc.upper() == identyfikator:
            dane = {}
            for key, value in fields.items():
                if 'arrayValue' in value:
                    lista = value['arrayValue'].get('values', [])
                    dane[key] = [el.get('stringValue', '') for el in lista]
                else:
                    for value_type in value:
                        dane[key] = value[value_type]

            # Wyświetlanie znalezionych danych
            print(f"\nDANE POJAZDU ({pole} = {identyfikator}):")
            for k, v in dane.items():
                if isinstance(v, list):
                    print(f"{k}: {', '.join(v)}")
                else:
                    print(f"{k}: {v}")
            print("-" * 40)
            znaleziono = True
            break

    if not znaleziono:
        print(f"Nie znaleziono pojazdu o {pole} = {identyfikator}.")

# Przykład użycia funkcji
wyswietl_dane_osoby()
wyswietl_dane_pojazdu()
