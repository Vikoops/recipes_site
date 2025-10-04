# users/views.py
from django.http import HttpResponse

def login_stub(request):
    return HttpResponse("<h1>Страница авторизации (заглушка)</h1>")

def logout_stub(request):
    return HttpResponse("<h1>Страница выхода (заглушка)</h1>")
