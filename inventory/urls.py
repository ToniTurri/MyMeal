from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/<str:name>', views.add_view, name='add'),
    path('remove/<int:pk>', views.remove_view, name='remove'),
    path(r'^update/(?P<pk>[0-9])/(?P<quantity>-?[0-9])', views.update_view, name='update'),
]