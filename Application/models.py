from django.db import models
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    PATROL_STATUS_CHOICES = [
        ('wolny', 'Wolny'),
        ('w_drodze', 'W drodze'),
        ('awaria', 'Awaria'),
        ('poza_pojazdem', 'Poza pojazdem'),
    ]
    patrol_status = models.CharField(max_length=20, choices=PATROL_STATUS_CHOICES, default='wolny')

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)  # null = do wszystkich
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

# Upewnij się, że profil tworzy się automatycznie (możesz użyć sygnałów post_save)
