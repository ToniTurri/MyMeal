from django.urls import path

from . import views

app_name = 'groceryList'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.GroceryListView.as_view(), name='detail'),
    path('new/', views.NewGroceryListView.as_view(), name='new'),
    path('new/<str:food_name>', views.NewGroceryListView.as_view(), name='new'),
    path('add/', views.add, name='add'),
    path('<int:pk>/add_to_list/', views.add_to_list, name='add_to_list'),

    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('new_recipe/', views.NewRecipeView.as_view(), name='new_recipe'),
    path('recipe/<int:pk>/', views.RecipeView.as_view(), name='recipe'),
    path('recipe/<int:pk>/add_to_recipe/', views.add_to_recipe, name='add_to_recipe'),
    path('<int:pk>/add_recipe_to_list/', views.add_recipe_to_list, name='add_recipe_to_list'),
    
    path('increment/', views.increment_food_item, name='increment_food_item'),
    path('decrement/', views.decrement_food_item, name='decrement_food_item'),

]
