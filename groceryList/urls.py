from django.urls import path

from . import views

app_name = 'groceryList'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('new/', views.new, name='new'),
    path('add/', views.add, name='add'),
    path('<int:list_id>/add_to_list/', views.add_to_list, name='add_to_list'),
]
