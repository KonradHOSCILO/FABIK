import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
_firestore_db = None
db = firestore.Client()


def pobierz_wiadomosci_dla_patrolu(patrol_id):
    global _firestore_db
    if _firestore_db is None:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _firestore_db = firestore.client()

    # Pobieramy dokumenty z kolekcji wiadomosci gdzie odbiorca == patrol_id lub == "all"
    docs = _firestore_db.collection('wiadomosci').where('odbiorca', 'in', [patrol_id, 'all']).stream()

    matching = []
    for doc in docs:
        data = doc.to_dict()
        matching.append({
            "nadawca": data.get("nadawca", ""),
            "odbiorca": data.get("odbiorca", ""),
            "tresc": data.get("tresc", ""),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else ""
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

    all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_messages
