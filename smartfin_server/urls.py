from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register', views.register, name='register'),
    path('api/auth/login', views.login_view, name='login'),
    path('api/upload', views.upload, name='upload'),
    path('api/data/', views.user_data, name='user_data'),
]
