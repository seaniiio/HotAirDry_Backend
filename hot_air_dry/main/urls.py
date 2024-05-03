from django.urls import path

from main import views

urlpatterns = [
    path('lot/',views.create_lot),
]