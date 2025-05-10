import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import random
from faker import Faker
from datetime import datetime

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
today = datetime.now().date()

# Słownik pojazdów
pojazdy_typy = {
    "samochód osobowy": {
        "Toyota": {
            "Corolla": {"nadwozia": ["sedan", "kombi"], "moc_min": 70, "moc_max": 140, "osoby": 5, "rok_start": 1995, "paliwa": ["benzyna", "diesel", "hybryda"]},
            "Yaris": {"nadwozia": ["hatchback"], "moc_min": 60, "moc_max": 120, "osoby": 5, "rok_start": 1999, "paliwa": ["benzyna", "hybryda"]},
        },
        "Volkswagen": {
            "Golf": {"nadwozia": ["hatchback"], "moc_min": 70, "moc_max": 180, "osoby": 5, "rok_start": 1995, "paliwa": ["benzyna", "diesel", "hybryda"]},
            "Passat": {"nadwozia": ["sedan", "kombi"], "moc_min": 85, "moc_max": 200, "osoby": 5, "rok_start": 1995, "paliwa": ["benzyna", "diesel", "hybryda"]},
        },
        "Ford": {
            "Focus": {"nadwozia": ["hatchback", "kombi"], "moc_min": 75, "moc_max": 150, "osoby": 5, "rok_start": 1998, "paliwa": ["benzyna", "diesel"]},
            "Mondeo": {"nadwozia": ["sedan", "kombi"], "moc_min": 85, "moc_max": 200, "osoby": 5, "rok_start": 1993, "paliwa": ["benzyna", "diesel", "hybryda"]},
        },
        "BMW": {
            "3 Series": {"nadwozia": ["sedan", "kombi", "coupe"], "moc_min": 100, "moc_max": 250, "osoby": 5, "rok_start": 1995, "paliwa": ["benzyna", "diesel"]},
            "5 Series": {"nadwozia": ["sedan", "kombi"], "moc_min": 120, "moc_max": 300, "osoby": 5, "rok_start": 1995, "paliwa": ["benzyna", "diesel", "hybryda"]},
        }
    },
    "motocykl": {
        "Yamaha": {
            "MT-07": {"nadwozia": ["naked"], "moc_min": 55, "moc_max": 75, "osoby": 2, "rok_start": 2014, "paliwa": ["benzyna"]},
            "R1": {"nadwozia": ["sport"], "moc_min": 110, "moc_max": 150, "osoby": 2, "rok_start": 1998, "paliwa": ["benzyna"]},
        },
        "Kawasaki": {
            "Z650": {"nadwozia": ["naked"], "moc_min": 50, "moc_max": 70, "osoby": 2, "rok_start": 2017, "paliwa": ["benzyna"]},
            "Ninja 400": {"nadwozia": ["sport"], "moc_min": 45, "moc_max": 60, "osoby": 2, "rok_start": 2018, "paliwa": ["benzyna"]},
        },
        "Honda": {
            "CBR500R": {"nadwozia": ["sport"], "moc_min": 35, "moc_max": 50, "osoby": 2, "rok_start": 2013, "paliwa": ["benzyna"]},
            "Africa Twin": {"nadwozia": ["adventure"], "moc_min": 70, "moc_max": 100, "osoby": 2, "rok_start": 1988, "paliwa": ["benzyna"]},
        }
    },
    "samochód ciężarowy": {
        "MAN": {
            "TGS": {"nadwozia": ["ciężarówka"], "moc_min": 250, "moc_max": 500, "osoby": 2, "rok_start": 2007, "paliwa": ["diesel"]},
        },
        "Volvo": {
            "FH": {"nadwozia": ["ciągnik siodłowy"], "moc_min": 300, "moc_max": 550, "osoby": 2, "rok_start": 2000, "paliwa": ["diesel"]},
        },
        "Mercedes-Benz": {
            "Actros": {"nadwozia": ["ciągnik siodłowy"], "moc_min": 300, "moc_max": 600, "osoby": 2, "rok_start": 1996, "paliwa": ["diesel"]},
        },
        "Scania": {
            "R Series": {"nadwozia": ["ciągnik siodłowy"], "moc_min": 350, "moc_max": 730, "osoby": 2, "rok_start": 2004, "paliwa": ["diesel"]},
        }
    },
    "ciągnik rolniczy": {
        "John Deere": {
            "6R": {"nadwozia": ["ciągnik"], "moc_min": 100, "moc_max": 250, "osoby": 1, "rok_start": 2010, "paliwa": ["diesel"]},
            "5M": {"nadwozia": ["ciągnik"], "moc_min": 75, "moc_max": 130, "osoby": 1, "rok_start": 2008, "paliwa": ["diesel"]},
        },
        "New Holland": {
            "T7": {"nadwozia": ["ciągnik"], "moc_min": 120, "moc_max": 280, "osoby": 1, "rok_start": 2012, "paliwa": ["diesel"]},
            "T5": {"nadwozia": ["ciągnik"], "moc_min": 75, "moc_max": 140, "osoby": 1, "rok_start": 2010, "paliwa": ["diesel"]},
        },
        "Zetor": {
            "Proxima": {"nadwozia": ["ciągnik"], "moc_min": 80, "moc_max": 120, "osoby": 1, "rok_start": 2004, "paliwa": ["diesel"]},
        }
    }
}

kolory = ["czarny", "biały", "srebrny", "czerwony", "niebieski", "zielony", "szary"]

for typ, marki in pojazdy_typy.items():
    for _ in range(25):  # dokładnie 25 pojazdów z każdego typu
        marka = random.choice(list(marki.keys()))
        model = random.choice(list(marki[marka].keys()))
        info = marki[marka][model]

        rocznik = random.randint(info["rok_start"], 2023)
        data_rejestracji = fake.date_between_dates(date_start=datetime(rocznik, 1, 1), date_end=today)

        paliwo = random.choice(info["paliwa"])
        czy_ma_lpg = random.choice([True, False]) if paliwo not in ["hybryda", "elektryczny"] else False

        data_badania = fake.date_between_dates(date_start=data_rejestracji, date_end=today.replace(year=today.year + 2))
        czy_badanie_wazne = data_badania >= today

        data_ubezpieczenia = fake.date_between_dates(date_start=data_rejestracji, date_end=today.replace(year=today.year + 2))
        czy_ubezpieczony = data_ubezpieczenia >= today

        masa_wlasna = random.randint(900, 2500)
        masa_maks = masa_wlasna + random.randint(300, 1500)

        moc_kW = random.randint(info["moc_min"], info["moc_max"])
        moc_KM = round(moc_kW * 1.35962)

        vin = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=17))
        tablica = fake.license_plate().replace(" ", "").upper()
        dowod_rejestracyjny = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))

        imie = fake.first_name()
        nazwisko = fake.last_name()
        pesel = fake.pesel()

        pojazd = {
            "utracony": random.choice([True, False]),
            "vin": vin,
            "tablica_rejestracyjna": tablica,
            "czy_badanie_techniczne_wazne": czy_badanie_wazne,
            "data_waznosci_badania": str(data_badania),
            "marka": marka,
            "model": model,
            "rocznik": rocznik,
            "kolor": random.choice(kolory),
            "nadwozie": random.choice(info["nadwozia"]),
            "czy_ubezpieczony": czy_ubezpieczony,
            "data_waznosci_ubezpieczenia": str(data_ubezpieczenia),
            "typ_pojazdu": typ,
            "dopuszczalny_nacisk_osi": round(random.uniform(2.0, 11.5), 1),
            "czy_ma_lpg": czy_ma_lpg,
            "czy_ma_hak": random.choice([True, False]),
            "nr_dowodu_rejestracyjnego": dowod_rejestracyjny.upper(),
            "data_pierwszej_rejestracji": str(data_rejestracji),
            "masa_wlasna": masa_wlasna,
            "masa_dopuszczalna": masa_maks,
            "dozwolona_ilosc_osob": info["osoby"],
            "moc_kW": moc_kW,
            "moc_KM": moc_KM,
            "rodzaj_paliwa": paliwo,
            "imie_wlasciciela": imie,
            "nazwisko_wlasciciela": nazwisko,
            "pesel_wlasciciela": pesel
        }

        # Nazwa dokumentu to tablica + VIN
        doc_id = f"{tablica}"
        db.collection("pojazdy").document(doc_id).set(pojazd)

print("Wygenerowano po 25 pojazdów każdego typu. Dokumenty mają nazwę: TABLICA")
