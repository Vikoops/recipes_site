from django.urls import path, re_path
from . import views
from .views import (
    IndexView, AboutView, RecipeDetailView,
    RecipesByCategoryView, RecipesByTagView,
    SuggestRecipeView, RecipeCreateView, RecipeUpdateView, RecipeDeleteView,
    RecipePublishView,
)

urlpatterns = [
    #path('', views.index, name='home'),
    path('', IndexView.as_view(), name='home'),
    #path('about/', views.about, name='about'),
    #path('recipe/<slug:slug>/', views.recipe_detail_slug, name='recipe_detail_slug'),

    
    #path("add/", views.add_recipe_model, name="add_recipe_model"),
    #path("suggest/", views.suggest_recipe, name="suggest_recipe"),
    #path('category/<slug:slug>/', views.recipes_by_category, name='recipes_by_category'),
    #path('tag/<slug:slug>/', views.recipes_by_tag, name='recipes_by_tag'),
    path('tags/', views.tag_list, name='tag_list'),
    path('stats/', views.stats, name='stats'),
    
    path('about/', AboutView.as_view(), name='about'),

    path('recipe/<slug:slug>/', RecipeDetailView.as_view(), name='recipe_detail_slug'),

    path('category/<slug:slug>/', RecipesByCategoryView.as_view(), name='recipes_by_category'),
    path('tag/<slug:slug>/', RecipesByTagView.as_view(), name='recipes_by_tag'),

    path('suggest/', SuggestRecipeView.as_view(), name='suggest_recipe'),
    path('add/', RecipeCreateView.as_view(), name='add_recipe_model'),   # было раньше — имя оставляем
    path('recipe/<slug:slug>/edit/', RecipeUpdateView.as_view(), name='recipe_edit'),
    path('recipe/<slug:slug>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('recipe/<slug:slug>/publish-toggle/', RecipePublishView.as_view(), name='recipe_publish_toggle'),
]
