
from typing import Any, Dict

MENU = [
    {"title": "Главная", "url_name": "home"},
    {"title": "Теги", "url_name": "tags_list"}, 
    {"title": "Статистика", "url_name": "stats"},
    {"title": "О сайте", "url_name": "about"},
    {"title": "Добавить рецепт", "url_name": "recipe_add"},
]

class DataMixin:
    
    title_page: str | None = None
    extra_context: Dict[str, Any] = {}

    paginate_by = 6  

    def __init__(self, *args, **kwargs):

        if self.title_page:
            self.extra_context["title"] = self.title_page
        
        if "menu" not in self.extra_context:
            self.extra_context["menu"] = MENU
        super().__init__(*args, **kwargs)

    def get_mixin_context(self, context: Dict[str, Any], **kwargs):
       
        if self.title_page:
            context["title"] = self.title_page
        context.setdefault("menu", MENU)
        context.setdefault("cat_selected", None)
        context.update(kwargs)
        return context
