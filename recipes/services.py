from django.db.models import Q
from .models import Recipe

def create_recipe(*, title:str, slug:str, desc:str='', image:str='', cook_time:str='', difficulty:str='easy', is_published:bool=True) -> Recipe:
    return Recipe.objects.create(
        title=title, slug=slug, desc=desc, image=image,
        cook_time=cook_time, difficulty=difficulty, is_published=is_published
    )

def read_all():
    return Recipe.objects.all()

def read_published():
    return Recipe.published.all()

def update_recipe(slug:str, **fields) -> Recipe:
    obj = Recipe.objects.get(slug=slug)
    for k, v in fields.items():
        setattr(obj, k, v)
    obj.save()
    return obj

def delete_recipe(slug:str) -> int:
    return Recipe.objects.filter(slug=slug).delete()[0]

def filter_search_sort(*, q:str='', difficulty:str='', is_published:bool|None=None, order:str='-created_at'):
    """
    Выборка + фильтрация + сортировка.
    q — поиск по названию/описанию, difficulty — 'easy'|'medium'|'hard',
    is_published — True/False/None, order — поле сортировки (например 'title' или '-created_at').
    """
    qs = Recipe.objects.all()
    if is_published is not None:
        qs = qs.filter(is_published=is_published)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(desc__icontains=q))
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    return qs.order_by(order)
