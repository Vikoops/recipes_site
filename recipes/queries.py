from django.db import models
from django.db.models import Q, F, Value, Count, Avg, Min, Max
from django.db.models.functions import Concat, Cast
from .models import Recipe, Category, Tag


def demo_queries():
    out = {}

    # 1) Поиск с Q: "суп" в названии или описании среди опубликованных
    out['search_soup'] = list(
        Recipe.published
        .filter(Q(title__icontains='суп') | Q(desc__icontains='суп'))
        .values('title', 'slug')
    )

    # 2) Вычисляемое поле: "Название (N мин)" — приводим число к строке через Cast
    out['title_with_time'] = list(
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

    # 3) Группировка: сколько рецептов в каждой категории
    out['per_category'] = list(
        Category.objects
        .annotate(cnt=Count('recipes'))
        .values('name', 'cnt')
        .order_by('-cnt', 'name')
    )

    # 4) Агрегации времени готовки по категориям
    out['cook_stats'] = list(
        Recipe.objects
        .values('category__name')
        .annotate(
            avg=Avg('cook_time_min'),
            mn=Min('cook_time_min'),
            mx=Max('cook_time_min')
        )
        .order_by('category__name')
    )

    # 5) Кол-во «быстрых» рецептов (тег fast)
    try:
        fast = Tag.objects.get(slug='fast')
        out['fast_count'] = Recipe.published.filter(tags=fast).count()
    except Tag.DoesNotExist:
        out['fast_count'] = 0

    return out
