from django.db import models

class Cart(models.Model):
    buyer = models.PositiveBigIntegerField(db_index=True)
    item_id = models.PositiveBigIntegerField(db_index=True)
    item_count = models.PositiveSmallIntegerField()
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer}'s cart"