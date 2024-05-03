from django.db import models

# Create your models here.

class Lot(models.Model):
    lot_id = models.PositiveSmallIntegerField(unique = True, null=False)
    normal_amount = models.IntegerField(default = 0, null=False)
    total_amount = models.IntegerField(default = 0, null=False)
    temperature_contribution = models.FloatField(default = 0.0, null=False)
    current_contribution = models.FloatField(default = 0.0, null=False)
    temperature_tendency = models.PositiveSmallIntegerField(default=50, null=False)
    current_tendency = models.PositiveSmallIntegerField(default=50, null=False)
    solution = models.CharField(max_length = 40)

    def __str__(self):
        return str(self.lot_id)