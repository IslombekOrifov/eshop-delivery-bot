from modeltranslation.translator import register, TranslationOptions
from .models import *

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)
    

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'about')
    
