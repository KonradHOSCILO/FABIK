import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Załaduj zmienne środowiskowe
load_dotenv()

# Ścieżka do pliku z poświadczeniami
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path:
    raise ValueError("Ścieżka do pliku .json nie została ustawiona w pliku .env")

# Inicjalizacja Firestore
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Tworzymy 10 patroli: 601-610
for i in range(601, 611):
    kryptonim = str(i)
    db.collection("patrole").document(kryptonim).set({
        "kryptonim": kryptonim,
        "status": "wolny",  # np. domyślny status
        "lokalizacja": None  # możemy dodać to później
    })

print("Dodano 10 patroli do kolekcji 'Patrole'.")
