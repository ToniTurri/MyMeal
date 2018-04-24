from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.RecipeView.as_view(), name='detail'),
    #path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('new_recipe/', views.add_recipe, name='new_recipe'),
]
