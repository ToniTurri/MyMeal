from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'stats'
urlpatterns = [
    path('', login_required(views.statsHandler), name='index')
]
