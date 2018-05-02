from django.urls import path

from . import views

app_name = 'groceryList'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.GroceryListView.as_view(), name='detail'),
    path('<int:pk>/update', views.update, name='update'),
]
