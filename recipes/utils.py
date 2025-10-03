# recipes/utils.py
from typing import Any, Dict

# Если у тебя меню рисуется «вручную» в base.html — ничего страшного,
# просто даём единое место, откуда потом будем подмешивать общий контекст.
MENU = [
    {"title": "Главная", "url_name": "home"},
    {"title": "Теги", "url_name": "tags_list"},      # если у тебя такой страницы нет — позже поправим/уберём
    {"title": "Статистика", "url_name": "stats"},
    {"title": "О сайте", "url_name": "about"},
    {"title": "Добавить рецепт", "url_name": "recipe_add"},
]

class DataMixin:
    """
    Общие настройки/контекст для CBV.
    Позже сюда добавим paginate_by и прочее.
    """
    title_page: str | None = None
    extra_context: Dict[str, Any] = {}

    # Можно задать дефолт для пагинации СРАЗУ, чтобы потом просто работало
    paginate_by = 6  # изменишь при желании

    def __init__(self, *args, **kwargs):
        # title в extra_context — «лениво» из атрибута класса
        if self.title_page:
            self.extra_context["title"] = self.title_page
        # меню добавляем, если его ещё не положили вручную
        if "menu" not in self.extra_context:
            self.extra_context["menu"] = MENU
        super().__init__(*args, **kwargs)

    def get_mixin_context(self, context: Dict[str, Any], **kwargs):
        """Удобный способ докинуть общий контент + то, что передали именованными аргументами."""
        if self.title_page:
            context["title"] = self.title_page
        context.setdefault("menu", MENU)
        context.setdefault("cat_selected", None)
        context.update(kwargs)
        return context
