from rest_framework import generics
from django.http import HttpResponse
from django.urls import reverse
from . import models
from . import serializers
from django.db.models import Q


def home(request):
    # Здесь криво, но это вспомогательная менюшка, для примера не принципиально
    return HttpResponse('''
        <a href='{make_data}'>make_data</a> <br/>
        <a href='{posts}'>posts</a> <br/>
        <a href='{posts}?q=vasya'>search only vasya</a> <br/>
        <a href='{posts}?q=Data+3'>search only Data 3</a> <br/>
    '''.format(
        make_data=reverse('make_data'),
        posts=reverse('posts'),
    ))


def make_data(request):
    # вспомогательная штука чтобы вручную через админку не делать тестовые данные
    models.make_data()
    return HttpResponse('ok')


class PostListSearchView(generics.ListAPIView):
    # View для показа всех данных списком с возможностью поиска
    lookup_field = 'id'
    serializer_class = serializers.PostSerializer

    # Здесь аналогично retrieve view из прошлых примерах мы задаём как ходим в базу данных
    # Но тут уже более очевидно - нет никаких доп. фильтраций по lookup_field, но есть фильрация
    # по поисоковому запросу в опциональном параметре q из урла.
    def get_queryset(self):
        res = models.Post.objects.all()
        query = self.request.GET.get("q")
        if query is not None:
            res = res.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).distinct()
        return res
