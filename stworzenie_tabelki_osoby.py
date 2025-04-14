import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import random
from faker import Faker
from datetime import datetime

# Funkcja do generowania numeru PESEL
def generate_pesel(date_of_birth, gender):
    # Data urodzenia
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    year = birth_date.year % 100  # dwu-cyfrowy rok
    month = birth_date.month
    day = birth_date.day

    # Numer porządkowy (mężczyźni: 000-499, kobiety: 500-999)
    number = random.randint(0, 499) if gender == 'male' else random.randint(500, 999)

    # Składa numer PESEL (6 cyfr dla daty + 3 cyfry dla numeru porządkowego)
    pesel_base = f"{year:02d}{month:02d}{day:02d}{number:03d}"

    # Jeśli długość numeru PESEL jest mniejsza niż 10, to sprawdź, czy coś poszło nie tak
    if len(pesel_base) != 9:
        raise ValueError(f"Numer PESEL jest niepoprawny. Spodziewana długość to 9 cyfr, a otrzymano: {pesel_base}")

    # Algorytm do obliczenia cyfry kontrolnej PESEL
    weight = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    total = sum(int(pesel_base[i]) * weight[i] for i in range(9))  # Oblicz sumę dla pierwszych 9 cyfr
    control_digit = (10 - (total % 10)) % 10  # Cyfra kontrolna

    # Zwróć pełny numer PESEL (9 cyfr + cyfra kontrolna)
    return pesel_base + str(control_digit)

# Wczytaj zmienne środowiskowe
load_dotenv()
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not cred_path:
    raise ValueError("Brakuje ścieżki do pliku .json z poświadczeniami w pliku .env")

# Inicjalizacja Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
fake = Faker("pl_PL")

# Dane pomocnicze
ograniczenia_list = ["brak", "okulary", "soczewki", "alkomat"]
kategorie_lista = ["AM", "A1", "A2", "A", "B1", "B", "C1", "C", "D1", "D", "BE", "C1E", "CE", "D1E", "DE", "T"]

today = datetime.now().date()

for i in range(1, 101):  # Zmiana liczby generowanych osób na 100
    ma_pj = random.random() > 0.3  # 70% osób ma PJ

    # Generowanie płci na podstawie losowania
    gender = random.choice(['male', 'female'])

    # Wygenerowanie daty urodzenia
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
    date_of_birth = str(birth_date)

    # Generowanie numeru PESEL, który pasuje do daty urodzenia
    pesel = generate_pesel(date_of_birth, gender)

    osoba = {
        "pierwsze_imie": fake.first_name(),
        "drugie_imie": fake.first_name(),
        "nazwisko": fake.last_name(),
        "imie_ojca": fake.first_name_male(),
        "imie_matki": fake.first_name_female(),
        "nazwisko_rodowe_matki": fake.last_name(),
        "nazwisko_rodowe": fake.last_name(),
        "data_urodzenia": date_of_birth,
        "pesel": pesel,
        "adres_zamieszkania": fake.address(),
        "miejsce_urodzenia": fake.city(),
        "poszukiwana": random.choice([True, False])
    }

    # ➤ Dowód osobisty
    data_waznosci_do = random.choice([fake.future_date("+10y"), fake.past_date("-10y")])
    if data_waznosci_do < today:
        status_do = "nieważny"
        czy_do_wazny = False
    else:
        status_do = random.choice(["ważny", "skradziony"])
        czy_do_wazny = status_do == "ważny"

    osoba.update({
        "data_waznosci_do": str(data_waznosci_do),
        "status_do": status_do,
        "czy_do_wazny": czy_do_wazny,
        "nr_do": fake.bothify(text="???######"),
        "kto_wydal_do": fake.city()
    })

    # ➤ Prawo jazdy
    if ma_pj:
        data_waznosci_pj = random.choice([fake.future_date("+10y"), fake.past_date("-10y")])
        punkty_karne = random.randint(0, 30)

        # Logika statusu PJ
        if punkty_karne > 24:
            status_pj = "cofnięte"
        elif data_waznosci_pj < today:
            status_pj = "nieważny"
        else:
            status_pj = random.choice(["wydane", "zatrzymane"])

        osoba.update({
            "status_pj": status_pj,
            "data_waznosci_pj": str(data_waznosci_pj),
            "numer_pj": fake.bothify(text="###########"),
            "kategorie_uprawnien": random.sample(kategorie_lista, random.randint(1, 4)),
            "wymagania": random.choice(ograniczenia_list),
            "ilosc_punktow_karnych": punkty_karne
        })

    else:
        osoba["status_pj"] = "niewydane"

    # Zapis do Firestore z użyciem PESEL jako identyfikatora
    db.collection("osoby").document(pesel).set(osoba)

print("Dodano 100 osób do kolekcji 'osoby' w Firestore.")
