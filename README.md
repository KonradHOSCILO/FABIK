# FABIK

Aplikacja webowa wspomagająca kontrole drogowe dla Policji oraz drogówki oraz ich interwencje.

## Technologie
- Django + Django REST Framework
- Google Cloud (Firestore, Endpoints, Memorystore)
- Python

## Struktura
- API – REST do obsługi pojazdów, interwencji i wiadomości
- Frontend – szablony Django Templates
- Scrum jako system zarządzania

## Uruchomienie lokalne
```bash
git clone https://github.com/{Nick}/FABIK.git
cd FABIK
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
