from django.urls import path

from main import views

urlpatterns = [
    path('lot/new/<int:lot_id>',views.create_lot)
]