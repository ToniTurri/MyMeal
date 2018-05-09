from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'inventory'
urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('add/', login_required(views.add_view), name='add'),
    path('remove/<int:pk>', login_required(views.remove_view), name='remove'),
    path('update/<int:pk>/<int:quantity>', login_required(views.update_view), name='update'),
]