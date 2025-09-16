from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),

    # с конвертерами path:
    path('category/<int:cat_id>/', views.category_by_id, name='category_by_id'),
    path('category/<slug:cat_slug>/', views.category_by_slug, name='category_by_slug'),

    # год из 4 цифр
    re_path(r'^archive/(?P<year>[0-9]{4})/$', views.archive, name='archive'),
]
