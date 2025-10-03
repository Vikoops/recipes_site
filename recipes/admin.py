from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Recipe, Category, Tag, RecipeInfo


# ---------- ДЕЙСТВИЯ (Actions) ----------
@admin.action(description="Опубликовать выбранные рецепты")
def make_published(modeladmin, request, queryset):
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f"Опубликовано: {updated}", level=messages.SUCCESS)


@admin.action(description="Снять с публикации выбранные рецепты")
def make_unpublished(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f"Снято с публикации: {updated}", level=messages.WARNING)


@admin.action(description="Добавить тег «быстро» выбранным рецептам")
def add_fast_tag(modeladmin, request, queryset):
    fast, _ = Tag.objects.get_or_create(slug="fast", defaults={"name": "быстро"})
    for obj in queryset:
        obj.tags.add(fast)
    modeladmin.message_user(
        request,
        f"Тег «быстро» добавлен к {queryset.count()} рецептам.",
        level=messages.INFO,
    )


# ---------- СОБСТВЕННЫЙ ФИЛЬТР ----------
class CookingTimeFilter(admin.SimpleListFilter):
    title = "время готовки"
    parameter_name = "cook_len"

    def lookups(self, request, model_admin):
        return [
            ("short", "менее 30 мин"),
            ("mid", "30–45 мин"),
            ("long", "более 45 мин"),
        ]

    def queryset(self, request, qs):
        v = self.value()
        if v == "short":
            return qs.filter(cook_time_min__lt=30)
        if v == "mid":
            return qs.filter(cook_time_min__gte=30, cook_time_min__lte=45)
        if v == "long":
            return qs.filter(cook_time_min__gt=45)
        return qs


# ---------- INLINE ДЛЯ OneToOne ----------
class RecipeInfoInline(admin.StackedInline):
    model = RecipeInfo
    can_delete = True
    extra = 0
    max_num = 1


# ---------- ФОРМА (подписи/виджеты) ----------
class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = "__all__"
        widgets = {
            "desc": forms.Textarea(attrs={"rows": 6}),
        }
        labels = {
            "title": "Название",
            "slug": "Слаг",
            "desc": "Описание",
            "image": "Путь к изображению",
            "photo": "Фото",
            "cook_time": "Время (текст)",
            "cook_time_min": "Время (мин)",
            "difficulty": "Сложность",
            "is_published": "Опубликован",
            "category": "Категория",
            "tags": "Теги",
            "created_at": "Создано",
            "updated_at": "Обновлено",
        }


# ---------- РЕЦЕПТЫ ----------
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    save_on_top = True
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    inlines = [RecipeInfoInline]
    empty_value_display = "—"

    # «Русские» колонки/заголовки
    def title_ru(self, obj):
        return obj.title
    title_ru.short_description = "Название"
    title_ru.admin_order_field = "title"

    def category_ru(self, obj):
        return obj.category
    category_ru.short_description = "Категория"
    category_ru.admin_order_field = "category"

    def created_at_ru(self, obj):
        return obj.created_at
    created_at_ru.short_description = "Создано"
    created_at_ru.admin_order_field = "created_at"

    def short_desc(self, obj):
        if not obj.desc:
            return ""
        return (obj.desc[:60] + "…") if len(obj.desc) > 60 else obj.desc
    short_desc.short_description = "Описание (кратко)"

    def tag_list(self, obj):
        return ", ".join(obj.tags.values_list("name", flat=True)) or "—"
    tag_list.short_description = "Теги"

    def colored_difficulty(self, obj):
        colors = {"easy": "#1a7f37", "medium": "#b7791f", "hard": "#c53030"}
        return format_html(
            '<b style="color:{}">{}</b>',
            colors.get(obj.difficulty, "#444"),
            obj.get_difficulty_display(),
        )
    colored_difficulty.short_description = "Сложность"
    colored_difficulty.admin_order_field = "difficulty"

    # миниатюра загруженного фото
    def thumb(self, obj):
        if getattr(obj, "photo", None):
            return mark_safe(
                f"<img src='{obj.photo.url}' width='80' "
                "style='border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2)'>"
            )
        return "—"
    thumb.short_description = "Превью"

    # -------- Список --------
    list_display = (
        "title_ru",          # ← ОБЯЗАТЕЛЬНО есть в list_display
        "category_ru",
        "colored_difficulty",
        "cook_time_min",
        "is_published",
        "tag_list",
        "thumb",
        "created_at_ru",
    )

    # Кликабельная колонка(и) — ДОЛЖНА быть в list_display
    list_display_links = ("title_ru",)

    # Поиск / фильтры / сортировка
    ordering = ("-created_at",)
    search_fields = ("title", "desc", "slug")
    list_filter = (
        "is_published",
        "difficulty",
        "category",
        "tags",
        CookingTimeFilter,
        "created_at",
    )

    # Поля формы (группы)
    readonly_fields = ("created_at", "updated_at", "thumb")
    fieldsets = (
        ("Основное", {
            "fields": (
                ("title", "slug"),
                "desc",
                ("image", "photo"),
                ("cook_time", "cook_time_min"),
                ("difficulty", "is_published"),
            )
        }),
        ("Связи", {"fields": ("category", "tags")}),
        ("Служебное", {
            "fields": (("created_at", "updated_at", "thumb"),),
            "classes": ("collapse",),
        }),
    )

    # Действия
    actions = [make_published, make_unpublished, add_fast_tag]


# ---------- КАТЕГОРИИ ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    empty_value_display = "—"

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = "Рецептов"

    list_display = ("name", "slug", "recipe_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


# ---------- ТЕГИ ----------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    empty_value_display = "—"

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = "Рецептов"

    list_display = ("name", "slug", "recipe_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


# ---------- БРЕНДИНГ ----------
admin.site.site_header = "Рецепты — админ-панель"
admin.site.site_title = "Рецепты | Admin"
admin.site.index_title = "Управление сайтом рецептов"


