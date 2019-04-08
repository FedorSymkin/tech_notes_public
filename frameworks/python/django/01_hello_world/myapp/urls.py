# coding: utf8

"""
Файл создан вручную.
Это точки входа для маршрутизации внутри даннго под-приложения.
"""

from django.urls import path
from . import views

"""
Всё в таком же формате, как и в основном urls.py
Пример двух маршрутов. Важный момент: эти маршруты срабатывают при заходе на

http://127.0.0.1:8000/myapp/
http://127.0.0.1:8000/myapp/stuff

Как видно части /myapp/ здесь нет. Потому что root для этого под-приложения - это /myapp/
Т.е. сюда приходит path из внешнего urls.py с уже отрезанным /myapp/

Это похоже на понятие текущей директории в файловой системе.
"""
urlpatterns = [
    # views.home и views.stuff - это собственно и есть обработчики запросов по этим путям
    path('', views.home, name='myhome'),
    path('stuff', views.stuff, name='mystuff'),
]