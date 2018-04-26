from django.urls import path

from . import views

app_name = 'recipeFinder'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<str:id>', views.recipe_detail, name='recipe_detail'),
    path('inventory-check', views.inventoryCheck, name='inventory-check'),
    path('anything', views.anything, name='anything')
]
