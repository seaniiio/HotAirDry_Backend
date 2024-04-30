from django.contrib import admin

from .models import Lot, Measurement

# Register your models here.
admin.site.register(Lot)
admin.site.register(Measurement)
