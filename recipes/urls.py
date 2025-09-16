from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
]


