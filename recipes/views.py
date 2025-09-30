from django.db import models
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F, Value, Count, Avg, Min, Max
from django.db.models.functions import Concat, Cast
from django.shortcuts import render
from django.contrib import messages
from .models import Recipe, Category, Tag
from .forms import SuggestRecipeForm
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


def recipes_by_category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    recipes = Recipe.published.filter(category=cat).order_by('-created_at')
    ctx = {'title': f'Категория: {cat.name}', 'recipes': recipes, 'category': cat, 'year': 2025}
    return render(request, 'recipes/by_category.html', ctx)

def recipes_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    recipes = Recipe.published.filter(tags=tag).order_by('-created_at')
    ctx = {'title': f'Тег: {tag.name}', 'recipes': recipes, 'tag': tag, 'year': 2025}
    return render(request, 'recipes/by_tag.html', ctx)

def tag_list(request):
    # список тегов с количеством рецептов (аннотация + группировка)
    tags = Tag.objects.annotate(recipe_count=Count('recipes')).order_by('-recipe_count', 'name')
    return render(request, 'recipes/tag_list.html', {'tags': tags, 'title': 'Теги', 'year': 2025})

def stats(request):
    """
    Страница с примерами аннотаций/агрегаций/группировок.
    Всё считается на стороне БД.
    """
    # 1) Сколько рецептов в каждой категории
    per_category = (Category.objects
                    .annotate(cnt=Count('recipes'))
                    .values('name', 'cnt')
                    .order_by('-cnt', 'name'))

    cook_stats = (Recipe.objects
                  .values('category__name')
                  .annotate(avg=Avg('cook_time_min'), mn=Min('cook_time_min'), mx=Max('cook_time_min'))
                  .order_by('category__name'))

    per_difficulty = (Recipe.objects
                      .values('difficulty')
                      .annotate(cnt=Count('id'))
                      .order_by('-cnt'))

    samples = (
    Recipe.published
    .annotate(
        title_with_time=Concat(
            F('title'),
            Value(' ('),
            Cast(F('cook_time_min'), output_field=models.CharField()),
            Value(' мин)')
        )
    )
    .values('title_with_time', 'slug')[:5]
)

    ctx = {
        'title': 'Статистика',
        'per_category': list(per_category),
        'cook_stats': list(cook_stats),
        'per_difficulty': list(per_difficulty),
        'samples': list(samples),
        'year': 2025,
    }
    return render(request, 'recipes/stats.html', ctx)

def suggest_recipe(request):
    """
    Страница «Предложить рецепт». На этом шаге просто валидируем форму и показываем результат.
    """
    if request.method == "POST":
        form = SuggestRecipeForm(request.POST)
        if form.is_valid():
            # тут в Лабе 10 шаг 1 НИЧЕГО не сохраняем — просто показываем успех и выведем очищенные данные
            messages.success(request, "Спасибо! Форма валидна — данные приняты.")
            ctx = {"form": SuggestRecipeForm(), "cleaned": form.cleaned_data, "title": "Предложить рецепт", "year": 2025}
            return render(request, "recipes/suggest.html", ctx)
        else:
            messages.error(request, "Проверьте поля — есть ошибки.")
    else:
        form = SuggestRecipeForm()

    ctx = {"form": form, "title": "Предложить рецепт", "year": 2025}
    return render(request, "recipes/suggest.html", ctx)