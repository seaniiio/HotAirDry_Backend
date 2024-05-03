from django.urls import path

from main import views

urlpatterns = [
    path('lot/',views.create_lot),
    path('lots/', views.get_normal_prob),
    path('lot/cont/<int:lot_id>', views.get_contribution),
    path('solution/<int:lot_id>', views.get_solution),
]