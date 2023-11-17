from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UserConfig
from users.views import RegisterView, ProfileView, generate_new_password, verify_email

app_name = UserConfig.name

urlpatterns = [
    path('', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/genpassword/', generate_new_password, name='generate_new_password'),
    path('verification/<str:email>', verify_email, name='verify_email'),
]
