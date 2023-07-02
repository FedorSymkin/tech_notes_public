from rest_framework import generics
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from . import models
from . import serializers


def home(request):
    # Здесь криво, но это вспомогательная менюшка, для примера не принципиально
    return HttpResponse('''
        <a href='{make_data}'>make_data</a> <br/>
        <a href='{get_data_petya}'>get petya post</a> <br/>
        <a href='{post_new}'>create post by petya</a> <br/>
    '''.format(
        make_data=reverse('make_data'),
        get_data_petya=reverse('post_rud', args=[2]),
        get_data_vasya=reverse('post_rud', args=[9]),
        post_new=reverse('post_new'),
    ))


def make_data(request):
    # вспомогательная штука чтобы вручную через админку не делать тестовые данные
    models.make_data()
    return HttpResponse('ok')


class PostRUDView(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, Update, Destroy в Django REST framework очень похожи и делаются одним общим view классом.
    # Почему? А вот почему: то, нужно сделать с данными (получить, обновить, удалить) определяется
    # методом http - GET, PUT/PATCH, DELETE, а url и ответ в виде json - одинаковый.ы
    #
    # Т.е.
    #     GET /post/2 - просто вернёт json
    #     PUT /post/2 - в теле запроса передаётся json для перезаписывания всей строки в таблице post.
    #        И тоже вернёт json (обновлённую запись)
    #     PATCH /port/2 - в теле запроса передаётся json, который содержит только те поля, которые надо поменять
    #        Остальное не трогаем. И тоже вернёт json (обновлённую запись)
    #     DELETE /port/2 - сабж.
    #
    # В этом проекте включен отладочный html, т.е. если перейти на /post/<id> в браузере, появится формочка
    # для отправки нужных запросов

    lookup_field = 'id'
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return models.Post.objects.all()


class PostCreateView(generics.CreateAPIView):
    # На отдельный обработчик /post/new повешен CreateAPIView
    # (хотя это можно было добавить в PostRUDView, добавив туда специальный CreateMixin,
    # но пусть будет так для большей наглядности)
    serializer_class = serializers.PostSerializer

    # Важная штука - мы здесь перехватываем управление при создании записи, чтобы добавить обязательное поле -
    # автор поста.
    # В оригинальном виде внутри CreateAPIView этот метод выглядит так:
    #
    # def perform_create(self, serializer):
    #    serializer.save()
    #
    # Напомню что в параметре author=petya author - это не зарезервированное поле, а просто обычное поле таблицы,
    # которое мы сами определили в модели.
    #
    # Пример логина пользователей будет дальше, а здесь пока пусть все посты будет создавать петя.

    # В этом проекте включен отладочный html, т.е. если перейти на /post/new в браузере, формально ответ будет
    # ошибкой (потому что Create это не GET), но будет и формочка для отправки POST
    def perform_create(self, serializer):
        petya = User.objects.filter(username='petya').first()
        serializer.save(author=petya)
