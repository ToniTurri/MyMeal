from django.urls import path, re_path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_view, name='add'),
    path('remove/<int:pk>', views.remove_view, name='remove'),
    re_path(r'^update/(?P<pk>[0-9])/(?P<quantity>-?[0-9])', views.update_view, name='update'),
]