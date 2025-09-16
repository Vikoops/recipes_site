from django.shortcuts import render
from django.http import HttpResponse

MENU = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
]

RECIPES_DB = [
    {
        'id': 1,
        'title': 'Шоколадный брауни',
        'image': 'recipes/images/ChocolateBrownie.png',
        'desc': 'Плотный и влажный брауни с насыщенным шоколадным вкусом.',
        'cook_time': '45 мин',
        'difficulty': 'средняя',
        'is_published': True,
    },
    {
        'id': 2,
        'title': 'Томатный суп',
        'image': 'recipes/images/TomatoSoup.png',
        'desc': 'Классический томатный суп с базиликом и чесноком.',
        'cook_time': '30 мин',
        'difficulty': 'простая',
        'is_published': True,
    },
    {
        'id': 3,
        'title': 'Смузи из манго',
        'image': None,
        'desc': 'Освежающий смузи. (Скрыт для примера фильтрации).',
        'cook_time': '5 мин',
        'difficulty': 'простая',
        'is_published': False,
    },
]

def index(request):
    ctx = {
        'title': 'Новые рецепты',
        'menu': MENU,
        'recipes': [r for r in RECIPES_DB if r['is_published']],
        'year': 2025,
    }
    return render(request, 'recipes/index.html', ctx)

def about(request):
    return render(request, 'recipes/about.html', {'title': 'О сайте', 'year': 2025})

def recipe_detail(request, recipe_id: int):
    rec = next((r for r in RECIPES_DB if r['id'] == recipe_id), None)
    if not rec:
        return HttpResponse("Рецепт не найден", status=404)
    return HttpResponse(f"<h1>{rec['title']}</h1><p>{rec['desc']}</p>")
