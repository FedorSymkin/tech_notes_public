from rest_framework import generics
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from . import models
from . import serializers


def home(request):
    # Здесь криво, но это вспомогательная менюшка, для примера не принципиально
    return HttpResponse('''
        <a href='{make_data}'>make_data</a> <br/>
        <a href='{get_data_petya}'>get petya post</a> <br/>
        <a href='{get_data_vasya}'>get vasya post</a> <br/>
        <a href='{get_not_existing_post}'>get_not_existsing_post</a> <br/>
    '''.format(
        make_data=reverse('make_data'),
        get_data_petya=reverse('viewpost', args=[2]),
        get_data_vasya=reverse('viewpost', args=[9]),
        get_not_existing_post=reverse('viewpost', args=[999]),
    ))


def make_data(request):
    # вспомогательная штука чтобы вручную через админку не делать тестовые данные
    models.make_data()
    return HttpResponse('ok')


# Вот наш API view для получения конкретного поста блога.
# Он наследуется от RetrieveAPIView. Этот view реализует тривиальную логику - получить
# конкретный объект из БД, перевести его в json и отдать. Есть и другие стандартные классы API views,
# подробнее в следующих примерах
class PostView(generics.RetrieveAPIView):

    # Тут мы говорим, как называется перемнная из урла, в которой первичный ключ, который мы ищем (см. urls.py)
    lookup_field = 'id'

    # Это обязательно (в отличие от обычных view). Определяет как конкретно заполнять данными наш json
    serializer_class = serializers.PostSerializer

    # Это тоже обязательно - как ходить в базу за данными.
    # Здесь тонкий момент, нечевидный сразу - мы отдали django запрос "дай все записи таблицы post"
    # Но на самом деле к запросу добавится WHERE id = <наш id из урла>. Т.е. тут мы отдаём как бы не запрос,
    # а шаблон запроса, в которому добавится поиск по конкретному id.
    # Ничего не мешает здесь отдать какой-то запрос с фильтрацией, и тогда в WHERE добавится условие AND id = ...
    def get_queryset(self):
        return models.Post.objects.all()

    # Это опциональная штука - когда мы в работу Serializer-а (которая начинается после извлечения данных из базы)
    # хотим что-то пробросить из view, например в данном случае request от пользователя
    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    # заметим также, что здесь с отличие от обычных views, нет прямой связи с моделью: model = models.Post,
    # Cвязь с моделями только через get_request.
    # Т.е.: если мы тут поставим models.SomeElse.objects.all() - ничего не упадёт, а просто в
    # serializer приедет другой объект - не Post, а SomeElse.
    # Как в этом случае себя поведёт Serializer - пока не исследовал.
