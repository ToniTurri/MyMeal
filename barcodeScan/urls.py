from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'barcodeScan'
urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('confirm/', login_required(views.add_to_list), name='add_to_list'),
    path('add/inv/<str:barcode>', login_required(views.add_to_inventory), name='add_to_inventory'),
    path('add/grocery/<str:barcode>', login_required(views.add_to_list), name='add_to_list'),
]