from django.urls import path

from . import views

app_name = 'barcodeScan'
urlpatterns = [
    path('', views.index, name='index'),
    path('confirm/', views.add_to_list, name='add_to_list'),
    path('add/inv/<str:barcode>', views.add_to_inventory, name='add_to_inventory'),
    path('add/grocery/<str:barcode>', views.add_to_list, name='add_to_list'),
]