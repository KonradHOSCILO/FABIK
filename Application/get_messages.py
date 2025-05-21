#Import modułu systemowego do interakcji z so, np. odczyt zmian środowiskowych,
import os
#wczytywanie zmiennych środowiskowych z .env
from dotenv import load_dotenv
#główny pakiet firebase admin sdk
import firebase_admin
#konkretne podmoduły
from firebase_admin import credentials, firestore


load_dotenv()
#tworzy globalną zmienną dla instancji firestore
_firestore_db = None
#tworzy klienta firestore
db = firestore.Client()


def pobierz_wiadomosci_dla_patrolu(patrol_id):
    #umożliwia modyfikowanie zmiennej firestore_db
    global _firestore_db
    #jeżeli nie ma połączenia z firestore to łączy
    if _firestore_db is None:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _firestore_db = firestore.client()

    #pobieramy dokumenty z kolekcji wiadomosci gdzie odbiorca == patrol_id lub == "all"
    docs = _firestore_db.collection('wiadomosci').where('odbiorca', 'in', [patrol_id, 'all']).stream()
    #tworzy pustą listę matching i dla każdego dokumentu doc, zamienia go na słownik data
    matching = []
    for doc in docs:
        data = doc.to_dict()
        matching.append({
            "nadawca": data.get("nadawca", ""),
            "odbiorca": data.get("odbiorca", ""),
            "tresc": data.get("tresc", ""),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else ""
            #Dodaje przetworzony słownik do listy matching, konwertując znacznik czasu na format ISO.
        })

    # Sortowanie malejąco po timestamp
    matching.sort(key=lambda x: x["timestamp"], reverse=True)
    return matching


def pobierz_wszystkie_wiadomosci():
    global _firestore_db
    if _firestore_db is None:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _firestore_db = firestore.client()
    #pobiera dokumenty z kolekcji wiadomosci
    docs = _firestore_db.collection('wiadomosci').stream()

    all_messages = []
    for doc in docs:
        data = doc.to_dict()
        all_messages.append({
            "nadawca": data.get("nadawca", ""),
            "odbiorca": data.get("odbiorca", ""),
            "tresc": data.get("tresc", ""),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else ""
        })
    #sortuje wszystkie wiadomości malejąco po timestamp i zwraca listę
    all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_messages
