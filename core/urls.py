from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('get-cities/', views.get_cities, name='get_cities'),
    path('test-messages/', views.test_messages, name='test_messages'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('test-upload/', views.test_upload, name='test_upload'),
    path('change-password/', views.change_password, name='change_password'),
] 