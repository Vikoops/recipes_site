from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('recipe/<slug:slug>/', views.recipe_detail_slug, name='recipe_detail_slug'),

    path("suggest/", views.suggest_recipe, name="suggest_recipe"),
    path('category/<slug:slug>/', views.recipes_by_category, name='recipes_by_category'),
    path('tag/<slug:slug>/', views.recipes_by_tag, name='recipes_by_tag'),
    path('tags/', views.tag_list, name='tag_list'),
    path('stats/', views.stats, name='stats'),
]
