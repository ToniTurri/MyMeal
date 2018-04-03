"""mealapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.simple.views import RegistrationView
from django.contrib.auth import views as auth_views

# Create a new class that redirects the user to the index page, 
# if successful at logging into o the application.
# This is for login and registration redirect.
class MyRegistrationView(RegistrationView):
    def get_success_url(request, user):
        return '/dashboard/'

urlpatterns = [
    path('groceryList/', include('groceryList.urls')),
    path('barcode/', include('barcodeScan.urls')),
    path('search/', include('recipeFinder.urls')),
    path('admin/', admin.site.urls),
    path('accounts/register/', MyRegistrationView.as_view(form_class=RegistrationFormUniqueEmail), name='registration_register'),
    path('accounts/', include('registration.backends.simple.urls')),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('dashboard/', include('dashboard.urls'))
]
