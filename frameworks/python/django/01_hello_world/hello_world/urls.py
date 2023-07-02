# coding: utf8

"""
Это главная точка входа http-сервера. Здесь прописывается маршрутизация путей в обработчики ответов.




hello_world URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.contrib import admin
from django.urls import path, include

# urlpatterns технически это зарезервированное название переменной, которую читает django
urlpatterns = [
    # Это стояло по умолчанию - по пути /admin будет станадартная админка django, но этого позже дойдём
    path('admin/', admin.site.urls),

    # А вот тут мы маршрутизируем путь /myapp в под-приложение, которое называется myapp
    # и в качестве точки входа этого под-приложения используем файл myapp/urls.py
    path('myapp/', include('myapp.urls')),

    # Демонстрация того, что мы это же самое под-приложение можем засунуть и в другой путь
    path('myapp2/', include('myapp.urls')),

    # Заметим также, что маршрута по умолчанию (т.е. по пути '') нет, поэтому http://127.0.0.1:8000/
    # выдаст ошибку.
]
