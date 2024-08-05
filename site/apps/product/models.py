from django.db import models
from django.utils.text import slugify
from django.urls import reverse_lazy

from uuid import uuid4


class CreatedUpdateBase(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        

class Category(CreatedUpdateBase):
    title = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', related_name='childs', on_delete=models.PROTECT, blank=True, null=True)
    
    def __str__(self):
        return self.title


class Product(CreatedUpdateBase):
    title = models.CharField(max_length=150)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT,)
    photo = models.ImageField(upload_to='products/')
    about = models.CharField(max_length=200, blank=True, null=True)
    price = models.PositiveBigIntegerField()
    min_count = models.PositiveIntegerField()
    measure = models.CharField(max_length=10)
    org_count_in_measure = models.PositiveIntegerField()
    org_measure = models.CharField(max_length=10)
    mxik = models.CharField(max_length=19)
    units_code = models.PositiveBigIntegerField(help_text="O'lchov birligi kodi, bugalterdan so'rash kerak")
  
    
    
    def __str__(self):
        return self.title