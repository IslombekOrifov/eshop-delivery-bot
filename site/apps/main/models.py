from django.db import models

from apps.common.validators import phone_number_validator


class Office(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='office/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self) -> str:
        return self.address