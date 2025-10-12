from django.urls import path
from . import views
from .views import (
    IndexView, AboutView, RecipeDetailView,
    RecipesByCategoryView, RecipesByTagView,
    SuggestRecipeView, RecipeCreateView, RecipeUpdateView, RecipeDeleteView,
    RecipePublishView, CategoriesListView, CommentCreateView, ReactionToggleView,
)


urlpatterns = [
    path('', IndexView.as_view(), name='home'),

    # инфо-страницы/списки
    path('tags/', views.tag_list, name='tag_list'),
    path('stats/', views.stats, name='stats'),
    path('categories/', CategoriesListView.as_view(), name='categories'),
    path('about/', AboutView.as_view(), name='about'),

    # формы/действия
    path('suggest/', SuggestRecipeView.as_view(), name='suggest_recipe'),

    # >>> СОЗДАНИЕ РЕЦЕПТА ДОЛЖНО БЫТЬ ВЫШЕ СЛАГА <<<
    path('recipe/add/', RecipeCreateView.as_view(), name='recipe_add'),
    # (если хочешь оставить старый адрес /add/ — можно сделать редирект)
    # path('add/', RedirectView.as_view(pattern_name='recipe_add', permanent=False), name='add_recipe_model'),

    # редактирование/удаление/публикация
    path('recipe/<slug:slug>/edit/', RecipeUpdateView.as_view(), name='recipe_edit'),
    path('recipe/<slug:slug>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('recipe/<slug:slug>/publish-toggle/', RecipePublishView.as_view(), name='recipe_publish_toggle'),

    path('recipe/<slug:slug>/comment/', CommentCreateView.as_view(), name='comment_add'),
    path('recipe/<slug:slug>/react/', ReactionToggleView.as_view(), name='recipe_react'),
    # СПИСКИ ПО ФИЛЬТРАМ
    path('category/<slug:slug>/', RecipesByCategoryView.as_view(), name='recipes_by_category'),
    path('tag/<slug:slug>/', RecipesByTagView.as_view(), name='recipes_by_tag'),

    # СЛАГ ДОЛЖЕН ИДТИ ПОСЛЕДНИМ
    path('recipe/<slug:slug>/', RecipeDetailView.as_view(), name='recipe_detail_slug'),
]
