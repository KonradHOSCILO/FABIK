#import modelu uzytkownika z django
from django.contrib.auth.models import User
#kolejny mod typowy do tworzenia modeli od django
from django.db import models


# Tworzymy modele
class UserProfile(models.Model):
    #kady uytkownik ma swj profil, i jak zostanie usunięty to rpofil tez
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    PATROL_STATUS_CHOICES = [
        ('wolny', 'Wolny'),
        ('w_drodze', 'W drodze'),
        ('awaria', 'Awaria'),
        ('poza_pojazdem', 'Poza pojazdem'),
    ]
    patrol_status = models.CharField(max_length=20, choices=PATROL_STATUS_CHOICES, default='wolny')


class Message(models.Model):
    #obsługa wiadomości według profili uzytkownikow django
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    #format wiadomości
    content = models.TextField()
    #dodaje date utworzenia wiadomosci
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        #domyslne sortowanie wedlug daty malejace
        ordering = ['-timestamp']
