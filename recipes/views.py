from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Value, Count, Avg, Min, Max
from django.db.models.functions import Concat, Cast
from django.contrib import messages
from .models import Recipe, Category, Tag
from .forms import SuggestRecipeForm, RecipeModelForm
from .utils import DataMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView, DetailView, ListView, FormView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.urls import NoReverseMatch
from .forms import CommentForm
from .models import Comment
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .models import Reaction



MENU = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
]

def index(request):
    sort_by = request.GET.get('sort', '-created_at') 
    q = request.GET.get('q', '').strip()
    diff = request.GET.get('difficulty', '')  

    recipes = Recipe.published.all()  

    if q:
        recipes = recipes.filter(Q(title__icontains=q) | Q(desc__icontains=q))
    if diff in dict(Recipe.Difficulty.choices):
        recipes = recipes.filter(difficulty=diff)

    recipes = recipes.order_by(sort_by)

    ctx = {
        'title': 'Новые рецепты',
        'recipes': recipes,
        'sort_by': sort_by, 'q': q, 'diff': diff,
        'difficulty_choices': Recipe.Difficulty.choices,
        'year': 2025,
    }
    return render(request, 'recipes/index.html', ctx)



def recipe_detail_slug(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, is_published=True)
    return render(request, 'recipes/detail.html', {'recipe': recipe, 'title': recipe.title, 'year': 2025})


def recipes_by_category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    recipes = Recipe.published.filter(category=cat).order_by('-created_at')
    ctx = {'title': f'Категория: {cat.name}', 'recipes': recipes, 'category': cat, 'year': 2025}
    return render(request, 'recipes/by_category.html', ctx)

def recipes_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    recipes = Recipe.published.filter(tags=tag).order_by('-created_at')
    ctx = {'title': f'Тег: {tag.name}', 'recipes': recipes, 'tag': tag, 'year': 2025}
    return render(request, 'recipes/by_tag.html', ctx)

def tag_list(request):

    tags = Tag.objects.annotate(recipe_count=Count('recipes')).order_by('-recipe_count', 'name')
    return render(request, 'recipes/tag_list.html', {'tags': tags, 'title': 'Теги', 'year': 2025})

def stats(request):
    
    per_category = (Category.objects
                    .annotate(cnt=Count('recipes'))
                    .values('name', 'cnt')
                    .order_by('-cnt', 'name'))

    cook_stats = (Recipe.objects
                  .values('category__name')
                  .annotate(avg=Avg('cook_time_min'), mn=Min('cook_time_min'), mx=Max('cook_time_min'))
                  .order_by('category__name'))

    per_difficulty = (Recipe.objects
                      .values('difficulty')
                      .annotate(cnt=Count('id'))
                      .order_by('-cnt'))

    samples = (
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

    ctx = {
        'title': 'Статистика',
        'per_category': list(per_category),
        'cook_stats': list(cook_stats),
        'per_difficulty': list(per_difficulty),
        'samples': list(samples),
        'year': 2025,
    }
    return render(request, 'recipes/stats.html', ctx)

def suggest_recipe(request):
    
    if request.method == "POST":
        form = SuggestRecipeForm(request.POST)
        if form.is_valid():
 
            messages.success(request, "Спасибо! Форма валидна — данные приняты.")
            ctx = {"form": SuggestRecipeForm(), "cleaned": form.cleaned_data, "title": "Предложить рецепт", "year": 2025}
            return render(request, "recipes/suggest.html", ctx)
        else:
            messages.error(request, "Проверьте поля — есть ошибки.")
    else:
        form = SuggestRecipeForm()

    ctx = {"form": form, "title": "Предложить рецепт", "year": 2025}
    return render(request, "recipes/suggest.html", ctx)



def add_recipe_model(request):
    
    if request.method == "POST":
        form = RecipeModelForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save() 
            messages.success(request, "Рецепт добавлен (ModelForm).")
            return redirect(recipe.get_absolute_url())
        else:
            messages.error(request, "Исправьте ошибки формы.")
    else:
        form = RecipeModelForm()

    return render(request, "recipes/add_model.html", {"form": form, "title": "Добавить рецепт"})

class IndexView(DataMixin, ListView):
    
    model = Recipe
    template_name = 'recipes/index.html'
    context_object_name = 'recipes'
    title_page = 'Новые рецепты'  

    def get_queryset(self):
        sort_by = self.request.GET.get('sort', '-created_at')
        q = self.request.GET.get('q', '').strip()
        diff = self.request.GET.get('difficulty', '')

        qs = (Recipe.published
              .all()
              .annotate(
                  likes=Count('reactions', filter=Q(reactions__kind='like')),
                  dislikes=Count('reactions', filter=Q(reactions__kind='dislike')),
              )
              .select_related('category')  
              .prefetch_related('tags'))

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(desc__icontains=q))
        if diff in dict(Recipe.Difficulty.choices):
            qs = qs.filter(difficulty=diff)

        return qs.order_by(sort_by)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '').strip()
        diff = self.request.GET.get('difficulty', '')
        sort_by = self.request.GET.get('sort', '-created_at')

        ctx.update({
            'sort_by': sort_by,
            'q': q,
            'diff': diff,
            'difficulty_choices': Recipe.Difficulty.choices,
            'year': 2025,
        })

        tail_parts = []
        if q: tail_parts.append(f"q={q}")
        if diff: tail_parts.append(f"difficulty={diff}")
        if sort_by and sort_by != '-created_at': tail_parts.append(f"sort={sort_by}")
        ctx['query_tail'] = ('&' + '&'.join(tail_parts)) if tail_parts else ''
        add_url = None
        try:
            add_url = reverse('recipes:recipe_add') 
        except NoReverseMatch:
            try:
                add_url = reverse('recipe_add')     
            except NoReverseMatch:
                try:
                    add_url = reverse('add_recipe_model')
                except NoReverseMatch:
                    add_url = None

        ctx['add_recipe_url'] = add_url
        return self.get_mixin_context(ctx)

        



class AboutView(DataMixin, TemplateView):
    template_name = 'recipes/about.html'
    title_page = 'О сайте'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['year'] = 2025
        return self.get_mixin_context(ctx)

class RecipeDetailView(DataMixin, DetailView):
    model = Recipe
    template_name = 'recipes/detail.html'
    context_object_name = 'recipe'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        qs = Recipe.published.all()
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            qs = Recipe.objects.filter(models.Q(is_published=True) | models.Q(author=user))
        return qs

    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        self.title_page = self.object.title
        ctx['year'] = 2025

        comments_qs = self.object.comments.select_related('author').filter(is_active=True)
        ctx['comments'] = comments_qs

        if self.request.user.is_authenticated:
            ctx['comment_form'] = CommentForm()
        else:
            ctx['comment_form'] = None

        user_reaction = None
        if self.request.user.is_authenticated:
            user_reaction = self.object.reactions.filter(user=self.request.user).values_list('kind', flat=True).first()
        ctx['user_reaction'] = user_reaction


        return self.get_mixin_context(ctx)

class RecipesByCategoryView(DataMixin, ListView):
    model = Recipe
    template_name = 'recipes/by_category.html'
    context_object_name = 'recipes'
    allow_empty = True
    title_page = 'Рецепты по категории'

    def get_queryset(self):
        return (Recipe.published
                .filter(category__slug=self.kwargs['slug'])
                .annotate(
                    likes=Count('reactions', filter=Q(reactions__kind='like')),
                    dislikes=Count('reactions', filter=Q(reactions__kind='dislike')),
                )
                .order_by('-created_at') 
                .select_related('category')
                .prefetch_related('tags')
                
                )
    


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cat = Category.objects.filter(slug=self.kwargs['slug']).first()
        ctx['query_tail'] = ''
        return self.get_mixin_context(ctx, cat_selected=cat, current_category=cat, title=f'Категория: {cat.name if cat else ""}')

class RecipesByTagView(DataMixin, ListView):
    model = Recipe
    template_name = 'recipes/by_tag.html'
    context_object_name = 'recipes'
    allow_empty = True
    title_page = 'Рецепты по тегу'

    def get_queryset(self):
        return (Recipe.published
                .filter(tags__slug=self.kwargs['slug'])
                .annotate(
                    likes=Count('reactions', filter=Q(reactions__kind='like')),
                    dislikes=Count('reactions', filter=Q(reactions__kind='dislike')),
                ).order_by('-created_at') 
                .prefetch_related('tags','category')
                
                )


       

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tag = Tag.objects.filter(slug=self.kwargs['slug']).first()
        ctx['query_tail'] = ''
        return self.get_mixin_context(ctx, current_tag=tag, title=f'Тег: {tag.name if tag else ""}')

class SuggestRecipeView(DataMixin, FormView):
    template_name = 'recipes/suggest.html'
    form_class = SuggestRecipeForm
    success_url = reverse_lazy('suggest_recipe')
    title_page = 'Предложить рецепт'

    def form_valid(self, form):
        messages.success(self.request, "Спасибо! Форма валидна — данные приняты.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Проверьте поля — есть ошибки.")
        return super().form_invalid(form)

class RecipeCreateView(LoginRequiredMixin, DataMixin, CreateView):
    model = Recipe
    form_class = RecipeModelForm
    template_name = 'recipes/add_model.html'
    title_page = 'Добавить рецепт'
    login_url = 'users:login'
    redirect_field_name = 'next'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user  
        obj.save()
        form.save_m2m()
        messages.success(self.request, "Рецепт добавлен.")
        return redirect(obj.get_absolute_url())
    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки формы.")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

class RecipeUpdateView(LoginRequiredMixin, DataMixin, UpdateView, PermissionRequiredMixin):
    permission_required = 'recipes.change_recipe'
    raise_exception = True
    model = Recipe
    form_class = RecipeModelForm
    template_name = 'recipes/edit_model.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    title_page = 'Редактировать рецепт'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.has_perm('recipes.change_recipe'):
            return qs
        return qs.filter(author=user)

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Изменения сохранены.")
        return resp

    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки формы.")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

class RecipeDeleteView(LoginRequiredMixin, DataMixin, DeleteView, PermissionRequiredMixin):
    permission_required = 'recipes.delete_recipe'
    raise_exception = True
    model = Recipe
    template_name = 'recipes/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('home')
    title_page = 'Удалить рецепт'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.has_perm('recipes.delete_recipe'):
            return qs
        return qs.filter(author=user)

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Рецепт удалён.")
        return super().delete(request, *args, **kwargs)

class RecipePublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'recipes.can_publish'
    raise_exception = True  

    def post(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        recipe.is_published = not recipe.is_published
        recipe.save(update_fields=['is_published'])
        messages.success(
            request,
            "Рецепт опубликован." if recipe.is_published else "Рецепт снят с публикации."
        )
        return redirect(recipe.get_absolute_url())
    

class CategoriesListView(DataMixin, ListView):
    model = Category
    template_name = 'recipes/categories.html'
    context_object_name = 'categories'
    title_page = 'Категории'

    def get_queryset(self):
        return Category.objects.annotate(recipes_count=Count('recipes')).order_by('name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['year'] = 2025
        return self.get_mixin_context(ctx)
    

class CommentCreateView(LoginRequiredMixin, DataMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'recipes/comment_form.html'  
    def form_valid(self, form):
        recipe = get_object_or_404(Recipe, slug=self.kwargs['slug'])
        obj = form.save(commit=False)
        obj.recipe = recipe
        obj.author = self.request.user
        obj.save()
        messages.success(self.request, "Комментарий добавлен.")

        return redirect(f"{recipe.get_absolute_url()}#comments")

    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки в комментарии.")
        recipe = get_object_or_404(Recipe, slug=self.kwargs['slug'])
        return redirect(f"{recipe.get_absolute_url()}#comments")


@method_decorator(require_POST, name='dispatch')
class ReactionToggleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        kind = request.POST.get('kind')
        if kind not in ('like', 'dislike'):
            messages.error(request, "Некорректный тип реакции.")
            return redirect(f"{recipe.get_absolute_url()}#reactions")

        react = Reaction.objects.filter(recipe=recipe, user=request.user).first()

        if react is None:
            Reaction.objects.create(recipe=recipe, user=request.user, kind=kind)
            messages.success(request, "Готово!")
        else:
            if react.kind == kind:
                react.delete()
                messages.info(request, "Реакция снята.")
            else:
                react.kind = kind
                react.save(update_fields=['kind'])
                messages.success(request, "Обновлено!")

        return redirect(f"{recipe.get_absolute_url()}#reactions")
    

    
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        u = self.request.user
        return u.is_superuser or u.has_perm('recipes.can_moderate_comments') or (self.comment.author_id == u.id)

    def post(self, request, *args, **kwargs):
        recipe = self.comment.recipe
        self.comment.delete()
        messages.warning(request, "Комментарий удалён.")
        return redirect(f"{recipe.get_absolute_url()}#comments")