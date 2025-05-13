from django.contrib.auth.models import AbstractUser
from django.db import models

from django.db.models.signals import post_save  # Сигнал сохранения модели
from django.dispatch import receiver  # Декоратор для обработки сигналов
from allauth.account.models import EmailAddress  # Модель для хранения email

class CustomUser(AbstractUser):
    # Если не нужен username, переопределите:
    username = None  
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # Указываем поле для логина
    REQUIRED_FIELDS = []  # Обязательные поля при createsuperuser

    def __str__(self):
        return self.email

# Сигналы для автоматического создания EmailAddress
@receiver(post_save, sender=CustomUser)
def create_email_address(sender, instance, created, **kwargs):
    if created and not EmailAddress.objects.filter(user=instance, email=instance.email).exists():
        EmailAddress.objects.create(
            user=instance, 
            email=instance.email,
            verified=True,
            primary=True
        )
