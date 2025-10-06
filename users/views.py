# users/views.py
from django.http import HttpResponse
# users/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import PasswordChangeNoRepeatForm

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"
    login_url = "users:login"   # на всякий случай; берётся и из settings.LOGIN_URL

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # в шаблоне будет доступен request.user
        ctx["title"] = "Профиль"
        return ctx

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:profile")
    form_class = PasswordChangeNoRepeatForm   # <-- вот так
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
