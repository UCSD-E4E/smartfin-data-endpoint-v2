"""
URL configuration for smartfin_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/ensembles", views.get_ensembles, name="get_ensembles"),
    path("api/ensembles/<int:ensemble_id>", views.get_ensemble, name="get_ensemble"),
    path("api/ensembles/create", views.create_ensemble, name="create_ensemble"),
    path('api/sessions', views.get_sessions, name='get_sessions'),
    path('api/sessions/<int:session_id>', views.get_session, name='get_session'),
    path('api/sessions/create', views.create_session, name='create_session'),
]
