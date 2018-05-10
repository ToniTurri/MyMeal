from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'recipeFinder'
urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('detail/<str:id>/<str:course>/', login_required(views.recipe_detail), name='recipe_detail'),
    path('detail/<str:id>', login_required(views.recipe_detail), name='recipe_detail'),
    path('recipe_search', login_required(views.recipe_search), name='recipe_search'),
    path('suggestions', login_required(views.suggestions), name='suggestions')
]
