from django.urls import path

from . import views

app_name = 'recipeFinder'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<str:id>/<str:course>/', views.recipe_detail, name='recipe_detail'),
    path('detail/<str:id>', views.recipe_detail, name='recipe_detail'),
    path('recipe_search', views.recipe_search, name='recipe_search'),
    path('suggestions', views.suggestions, name='suggestions')
]
