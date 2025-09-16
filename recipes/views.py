from django.shortcuts import render

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect

def index(request):
    return HttpResponse("<h1>Главная: рецепты</h1><p>Добро пожаловать на сайт рецептов!</p>")

def about(request):
    return HttpResponse("<h1>О сайте</h1><p>Тут будут рецепты, категории, теги и поиск.</p>")

def archive(request, year: int):
    if year > 2023:
        return redirect('/', permanent=False)  # 302
    return HttpResponse(f"<h1>Архив рецептов</h1><p>Год: {year}</p>")

def category_by_id(request, cat_id: int):
    return HttpResponse(f"<h1>Категория #{cat_id}</h1>")

def category_by_slug(request, cat_slug: str):
    return HttpResponse(f"<h1>Категория: {cat_slug}</h1>")
