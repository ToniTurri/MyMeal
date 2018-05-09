from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'groceryList'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:pk>/', login_required(views.GroceryListView.as_view()), name='detail'),
    path('new/', login_required(views.NewGroceryListView.as_view()), name='new'),
    path('new/<str:food_name>/<str:barcode>', login_required(views.NewGroceryListView.as_view()), name='new'),
    path('add/', login_required(views.add), name='add'),
    path('<int:pk>/update', login_required(views.update), name='update'),
    path('<int:pk>/<int:id>/confirm', login_required(views.confirm_item), name='confirm_item'),
    path('<int:pk>/<int:id>/delete', login_required(views.delete_item), name='delete_item'),
    path('<int:pk>/delete', login_required(views.delete_list), name='delete_list')
]
