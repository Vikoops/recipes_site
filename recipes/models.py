from django.db import models
from django.urls import reverse
import os, uuid
from django.conf import settings


def recipe_photo_upload_to(instance, filename):
    # имя типа recipes/<uuid>.ext
    ext = os.path.splitext(filename)[1].lower()
    return f"recipes/{uuid.uuid4().hex}{ext}"

class PublishedManager(models.Manager):
    """Менеджер, показывающий только опубликованные рецепты."""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Category(models.Model):
    name = models.CharField("Название", max_length=120, unique=True, db_index=True)
    slug = models.SlugField("Слаг", max_length=120, unique=True, db_index=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("recipes_by_category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField("Название", max_length=120, unique=True, db_index=True)
    slug = models.SlugField("Слаг", max_length=120, unique=True, db_index=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("recipes_by_tag", kwargs={"slug": self.slug})


class Recipe(models.Model):
    """Основная модель рецепта."""
    class Difficulty(models.TextChoices):
        EASY = "easy", "простая"
        MEDIUM = "medium", "средняя"
        HARD = "hard", "сложная"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        null=True, blank=True,  # временно: потом при желании сделаем обязательным
        verbose_name='Автор'
    )

    title = models.CharField("Название", max_length=255, db_index=True)
    slug = models.SlugField("Слаг", max_length=255, unique=True, db_index=True)
    desc = models.TextField("Описание", blank=True)
    image = models.CharField("Путь к изображению", max_length=255, blank=True)  # путь в /static/...
    cook_time = models.CharField("Время (текст)", max_length=50, blank=True)     # например: "45 мин"
    cook_time_min = models.PositiveIntegerField("Время (мин)", default=0)        # число минут для агрегаций
    difficulty = models.CharField(
        "Сложность",
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    is_published = models.BooleanField("Опубликован", default=True)
    photo = models.ImageField("Фото", upload_to=recipe_photo_upload_to, blank=True, null=True)

    # Связи
    category = models.ForeignKey(
        "Category",
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )  # 1 категория -> много рецептов

    tags = models.ManyToManyField(
        "Tag",
        verbose_name="Теги",
        blank=True,
        related_name="recipes",
    )  # многие теги <-> многие рецепты

    # служебные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    # менеджеры
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]
        permissions = [
            ('can_publish', 'Может публиковать рецепты'),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("recipe_detail_slug", kwargs={"slug": self.slug})


class RecipeInfo(models.Model):
    """Доп.информация про рецепт (1 <-> 1)."""
    recipe = models.OneToOneField(
        "Recipe",
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="info",
    )
    calories = models.PositiveIntegerField("Калории (ккал/порция)", default=0)
    source_url = models.URLField("Источник", blank=True)

    class Meta:
        verbose_name = "Доп. информация о рецепте"
        verbose_name_plural = "Доп. информация о рецептах"

    def __str__(self) -> str:
        return f"Info for {self.recipe.title}"

