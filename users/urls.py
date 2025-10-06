# users/urls.py
from django.urls import path
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)

from .forms import EmailAuthenticationForm
from .views import ProfileView, UserPasswordChangeView

app_name = 'users'

urlpatterns = [
    # Вход / выход
    path(
        'login/',
        LoginView.as_view(
            template_name='users/login.html',
            authentication_form=EmailAuthenticationForm
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Профиль и смена пароля
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),

    # Восстановление пароля
    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.txt',
            subject_template_name='users/password_reset_subject.txt',
            success_url=reverse_lazy('users:password_reset_done'),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
