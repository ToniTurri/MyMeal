from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.RecipeView.as_view(), name='detail'),
    path('new_recipe/', views.add_recipe, name='new_recipe'),
    path('<int:pk>/edit', views.edit_recipe, name='edit_recipe'),
    path('<int:pk>/delete', views.delete_recipe, name='delete_recipe')
]
