import firebase_admin
from firebase_admin import credentials, firestore

# Zastąp to ścieżką do Twojego klucza JSON (plik z Firebase)
cred = credentials.Certificate("./credentials.json")

firebase_admin.initialize_app(cred)
db = firestore.client()
