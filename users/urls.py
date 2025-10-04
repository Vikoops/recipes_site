from django.urls import path
from . import views

app_name = 'users'  # нужно для пространства имён

urlpatterns = [
    path('login/', views.login_stub, name='login'),
    path('logout/', views.logout_stub, name='logout'),
]
