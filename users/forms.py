# users/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Пароль"})
    )

    error_messages = {
        "invalid_login": "Неверный e-mail или пароль.",
        "inactive": "Учетная запись отключена.",
        "not_unique": "В системе найдено несколько пользователей с этим e-mail. Обратитесь к администратору.",
    }

    def __init__(self, request=None, *args, **kwargs):
        # LoginView передает сюда request — сохраняем, дальше используем в authenticate()
        self.request = request
        super().__init__(*args, **kwargs)
        self.user_cache = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            # наш бекенд принимает email как username
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise ValidationError(self.error_messages["invalid_login"])
            if not user.is_active:
                raise ValidationError(self.error_messages["inactive"])
            self.user_cache = user
        return cleaned

    def get_user(self):
        return self.user_cache


class PasswordChangeNoRepeatForm(PasswordChangeForm):
    """Запрет смены пароля на тот же самый."""
    def clean_new_password2(self):
        new_password2 = super().clean_new_password2()
        old_password = self.cleaned_data.get("old_password")
        user = self.user  # устанавливается базовым PasswordChangeForm

        # если новый пароль совпадает со старым — запретим
        if old_password and user.check_password(new_password2):
            raise ValidationError("Новый пароль не должен совпадать с текущим.")
        return new_password2
    

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="E-mail",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"})
    )

    class Meta:
        model = User
        fields = ("username", "email",)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким e-mail уже зарегистрирован.")
        return email