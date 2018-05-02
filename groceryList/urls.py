from django.urls import path

from . import views

app_name = 'groceryList'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.NewGroceryListView.as_view(), name='new'),
    path('new/<str:food_name>', views.NewGroceryListView.as_view(), name='new'),
    path('add/', views.add, name='add'),
    path('<int:pk>/', views.GroceryListView.as_view(), name='detail'),
    path('<int:pk>/update', views.update, name='update'),
    path('<int:pk>/<int:id>/confirm', views.confirm_item, name='confirm_item'),
    path('<int:pk>/<int:id>/delete', views.delete_item, name='delete_item')
]
