from django.db import models
from django.urls import reverse


class PublishedManager(models.Manager):
    """Показывает только опубликованные рецепты."""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Category(models.Model):
    """Категория: Супы, Десерты, Салаты… (1 -> many Recipes)"""
    name = models.CharField(max_length=120, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes_by_category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Тег: 'быстро', 'шоколад', 'вегетарианское' (many <-> many Recipes)"""
    name = models.CharField(max_length=120, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes_by_tag', kwargs={'slug': self.slug})


class Recipe(models.Model):
    """Основная модель рецепта."""
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'простая'
        MEDIUM = 'medium', 'средняя'
        HARD = 'hard', 'сложная'

    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    desc = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)  # путь к статичному изображению
    cook_time = models.CharField(max_length=50, blank=True)  # строка "45 мин" для отображения
    cook_time_min = models.PositiveIntegerField(default=0)   # число минут для расчётов/агрегаций
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY
    )
    is_published = models.BooleanField(default=True)

    # Связи (в виде строк, чтобы не зависеть от порядка объявления классов)
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes'
    )  # 1 категория -> много рецептов

    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='recipes'
    )  # многие теги <-> многие рецепты

    # служебные поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # менеджеры
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # детальная страница по слагу
        return reverse('recipe_detail_slug', kwargs={'slug': self.slug})


class RecipeInfo(models.Model):
    """Доп.информация про рецепт (1 <-> 1)"""
    recipe = models.OneToOneField('Recipe', on_delete=models.CASCADE, related_name='info')
    calories = models.PositiveIntegerField(default=0)  # ккал на порцию
    source_url = models.URLField(blank=True)

    def __str__(self):
        return f'Info for {self.recipe.title}'
