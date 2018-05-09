from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'recipes'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:pk>/', login_required(views.RecipeView.as_view()), name='detail'),
    path('new_recipe/', login_required(views.add_recipe), name='new_recipe'),
    path('<int:pk>/edit', login_required(views.add_recipe), name='edit_recipe'),
    path('<int:pk>/delete', login_required(views.delete_recipe), name='delete_recipe'),
    path('<int:pk>/create_grocery_list/', login_required(views.create_grocery_list), name='create_grocery_list')
]
