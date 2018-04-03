from django.urls import path

from . import views

app_name = 'recipeFinder'
urlpatterns = [
    path('', views.index, name='index'),
]