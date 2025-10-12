from django import forms
from .models import Recipe, Category, Tag
from .models import Comment
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator

# наш пользовательский валидатор: запретим слово "рецепт" в названии
def validate_no_recipe_word(value: str):
    if "рецепт" in value.lower():
        raise ValidationError("Не пишите слово «рецепт» в названии — это и так понятно 🙂")

# ещё один пользовательский валидатор: в тексте не должно быть спама/запрещённых слов
BAD_WORDS = ("наркот", "бомба", "яд", "взрыв")
def validate_no_bad_words(value: str):
    low = value.lower()
    if any(bad in low for bad in BAD_WORDS):
        raise ValidationError("Текст содержит запрещённые слова.")

class SuggestRecipeForm(forms.Form):
    """Немодельная форма для шага 1 — просто валидируем данные пользователя."""
    DIFFICULTY_CHOICES = (
        ("easy",   "простая"),
        ("medium", "средняя"),
        ("hard",   "сложная"),
    )

    title = forms.CharField(
        label="Название",
        help_text="Коротко и по делу (5–60 символов).",
        validators=[MinLengthValidator(5), MaxLengthValidator(60), validate_no_recipe_word],
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Напр.: Томатный суп с базиликом"})
    )

    email = forms.EmailField(
        label="Ваш e-mail",
        help_text="Чтобы мы могли уточнить детали.",
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "name@example.com"})
    )

    cook_time_min = forms.IntegerField(
        label="Время готовки, минут",
        help_text="От 1 до 600.",
        validators=[MinValueValidator(1), MaxValueValidator(600)],
        widget=forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 600})
    )

    difficulty = forms.ChoiceField(
        label="Сложность",
        choices=DIFFICULTY_CHOICES,
        widget=forms.Select(attrs={"class": "form-input"})
    )

    desc = forms.CharField(
        label="Краткое описание",
        help_text="Не менее 20 символов.",
        validators=[MinLengthValidator(20), validate_no_bad_words],
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 5, "placeholder": "Опишите идею блюда…"})
    )

    # дополнительные «умные» проверки полей
    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        # пусть название начинается с буквы (не цифры/символа)
        if not title[0].isalpha():
            raise ValidationError("Название должно начинаться с буквы.")
        return title

    def clean(self):
        """Пример межполевой проверки."""
        cleaned = super().clean()
        title = cleaned.get("title", "")
        desc = cleaned.get("desc", "")
        if title and desc and title.lower() in desc.lower():
            # не критично, но покажем предупреждение в верхнем блоке ошибок
            raise ValidationError("Заголовок не должен полностью повторяться в описании.")
        return cleaned


def validate_no_super(value: str):
    if "супер" in value.lower():
        raise ValidationError("Избегайте слова «супер» в названии :)")

class RecipeModelForm(forms.ModelForm):
    """Шаг 2: форма, связанная с моделью Recipe (без загрузки файлов — это шаг 3)."""
    class Meta:
        model = Recipe
        fields = ['title','slug','desc','cook_time','cook_time_min',
          'difficulty','is_published','category','tags','photo', 'image']

        labels = {
            'title': 'Название',
            'slug': 'Слаг (латиница)',
            'desc': 'Описание',
            'cook_time': 'Время (текст)',
            'cook_time_min': 'Время (мин)',
            'difficulty': 'Сложность',
            'is_published': 'Опубликован',
            'category': 'Категория',
            'tags': 'Теги',
            'photo': 'Фото',

        }
        help_texts = {
            'slug': 'Только латинские буквы, цифры и дефисы. Должен быть уникальным.',
        }
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 5}),
        }

    # добавим встроенные + свои валидаторы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].validators += [MinLengthValidator(3), MaxLengthValidator(100), validate_no_super]
        self.fields['cook_time_min'].validators += [MinValueValidator(1), MaxValueValidator(600)]

    # пример доп. проверки поля
    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title[0].isalpha():
            raise ValidationError("Название должно начинаться с буквы.")
        return title

    # межполевой контроль: если cook_time пустой, но cook_time_min задан — всё ок, а вот наоборот — предупредим
    def clean(self):
        cleaned = super().clean()
        cook_text = (cleaned.get('cook_time') or '').strip()
        cook_min = cleaned.get('cook_time_min')

        # если минутa есть, а текст пустой — автозаполним "N мин"
        if cook_min and not cook_text:
            cleaned['cook_time'] = f"{cook_min} мин"

        # если наоборот: есть текст, а минут нет — оставляем (пользовательское описание),
        # но рекомендуем всё же заполнить минуты для статистики/фильтрации
        return cleaned

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите что-нибудь полезное…'}),
        min_length=5,
        error_messages={
            'required': 'Комментарий не может быть пустым.',
            'min_length': 'Комментарий слишком короткий (минимум 5 символов).',
        }
    )

    class Meta:
        model = Comment
        fields = ('body',)  # recipe/author выставим во вью
