from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'full_name', 'username', 'phone')
    list_display_links = ('id', 'full_name')
    ordering = ('id', 'full_name', 'username')
    search_fields = ['full_name', 'username', 'phone', 'telegram_id']
