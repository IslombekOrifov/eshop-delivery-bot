from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from .models import (
    Category, Product, 
)


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('title', 'parent', 'image')
    ordering = ('title',)


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('title', 'category', 'photo', 'price')
    ordering = ('category', 'price',)
    fieldsets = (
        ('Translateble', {
          'fields': ('title', 'about')
        }),
        ('Standard info', {
            'fields': ('category', 'photo', 'price', 'min_count', 'measure', 'org_count_in_measure', 'org_measure', 'mxik', 'units_code')
        }),
    )
