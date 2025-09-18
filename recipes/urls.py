from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('recipe/<slug:slug>/', views.recipe_detail_slug, name='recipe_detail_slug'),
]


