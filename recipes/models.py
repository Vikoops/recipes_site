from django.db import models
from django.urls import reverse

class PublishedManager(models.Manager):
    def get_queryset(self):

        return super().get_queryset().filter(is_published=True)

class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'простая'
        MEDIUM = 'medium', 'средняя'
        HARD = 'hard', 'сложная'

    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    desc = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)  
    cook_time = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()     
    published = PublishedManager()  

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe_detail_slug', kwargs={'slug': self.slug})
