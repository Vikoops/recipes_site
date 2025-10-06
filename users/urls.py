# users/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .forms import EmailAuthenticationForm
from .views import ProfileView, UserPasswordChangeView

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='users/login.html',
            authentication_form=EmailAuthenticationForm
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),

    # профиль + смена пароля
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
]
