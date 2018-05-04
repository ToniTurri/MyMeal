from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_view, name='add'),
    path('remove/<int:pk>', views.remove_view, name='remove'),
    path(r'update/<int:pk>/<int:quantity>', views.update_view, name='update'),
]