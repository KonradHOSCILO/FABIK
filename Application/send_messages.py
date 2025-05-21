import os
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized")

_firestore_db = firestore.client()


def wyslij_wiadomosc(nadawca, odbiorca, tresc):
    #pobiera biezacy czas
    timestamp = datetime.utcnow()
    #generuje id wiadomosci
    doc_id = f"{odbiorca}_{timestamp.strftime('%Y%m%dT%H%M%S%f')}"
    #sprawdza czy takie id juz istnieje, jak nie to tworzy
    doc_ref = _firestore_db.collection('wiadomosci').document(doc_id)
    doc_ref.set({
        'nadawca': nadawca,
        'odbiorca': odbiorca,
        'tresc': tresc,
        'timestamp': timestamp
    })
