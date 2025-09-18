from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Recipe
from django.db.models import Q

MENU = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
]

def index(request):
    sort_by = request.GET.get('sort', '-created_at')  # '-created_at' | 'title' | '-title'
    q = request.GET.get('q', '').strip()
    diff = request.GET.get('difficulty', '')  # 'easy'|'medium'|'hard'|''

    recipes = Recipe.published.all()  # базово — только опубликованные

    if q:
        recipes = recipes.filter(Q(title__icontains=q) | Q(desc__icontains=q))
    if diff in dict(Recipe.Difficulty.choices):
        recipes = recipes.filter(difficulty=diff)

    recipes = recipes.order_by(sort_by)

    ctx = {
        'title': 'Новые рецепты',
        'recipes': recipes,
        'sort_by': sort_by, 'q': q, 'diff': diff,
        'difficulty_choices': Recipe.Difficulty.choices,
        'year': 2025,
    }
    return render(request, 'recipes/index.html', ctx)

def about(request):
    return render(request, 'recipes/about.html', {'title': 'О сайте', 'year': 2025})

def recipe_detail_slug(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, is_published=True)
    return render(request, 'recipes/detail.html', {'recipe': recipe, 'title': recipe.title, 'year': 2025})
