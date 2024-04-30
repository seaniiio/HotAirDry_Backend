from django.db import models

# Create your models here.

class Lot(models.Model):
    lot_id = models.PositiveSmallIntegerField(unique = True)
    normal_prob = models.PositiveSmallIntegerField(default=50)
    abnormal_type = models.PositiveSmallIntegerField(default=50)
    temp_normal_prob = models.PositiveSmallIntegerField(default=50)
    current_normal_prob = models.PositiveSmallIntegerField(default=50)

class Measurement(models.Model):
    lot_id = models.ForeignKey(Lot, to_field='lot_id', on_delete=models.CASCADE)
    result_type = models.PositiveSmallIntegerField(default=0)
    abnormal_cause = models.PositiveSmallIntegerField(default=0)
    process = models.PositiveSmallIntegerField()
    # time = models.DateTimeField()
    temp = models.IntegerField()
    current = models.IntegerField()