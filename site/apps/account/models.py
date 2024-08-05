from django.db import models
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager, UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class TelegramUser(models.Model):
    full_name = models.CharField(verbose_name="Ism", max_length=100, blank=True, null=True, db_index=True)
    username = models.CharField(verbose_name="Telegram username", max_length=100, null=True, db_index=True)
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID', unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=2, default='ru')
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.telegram_id} - {self.full_name}"