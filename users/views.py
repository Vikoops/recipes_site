from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import PasswordChangeNoRepeatForm
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.shortcuts import redirect


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"
    login_url = "users:login"   

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Профиль"
        return ctx

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:profile")
    form_class = PasswordChangeNoRepeatForm  
    login_url = "users:login"

    def form_valid(self, form):
        messages.success(self.request, "Пароль успешно изменён.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки формы.")
        return super().form_invalid(form)
    
def login_stub(request):
    return HttpResponse("<h1>Страница авторизации (заглушка)</h1>")

def logout_stub(request):
    return HttpResponse("<h1>Страница выхода (заглушка)</h1>")


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("users:profile") 

    def form_valid(self, form):
    
        response = super().form_valid(form)
    
        user = authenticate(
            self.request,
            username=form.cleaned_data["email"],   
            password=form.cleaned_data["password1"]
        )
        if user is None:
        
            user = authenticate(
                self.request,
                username=self.object.username,
                password=form.cleaned_data["password1"]
            )
        if user:
            login(self.request, user)
            messages.success(self.request, "Регистрация успешна. Добро пожаловать!")

        nxt = self.request.GET.get("next")
        return redirect(nxt or self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки формы.")
        return super().form_invalid(form)