from rest_framework import serializers
from . import models


# Классы Serializers используются во views.
# Это по смыслу аналоги форм, если сравнивать с обычой html-выдачей
# Тут определяется в каком конкретно виде будут отданы данные (т.е. помимо формата json
# нужно рассказать django что именно мы хотим там отдавать)


# Это serializer для постов из нашего блога
class PostSerializer(serializers.ModelSerializer):
    # Смысл этих двух строчек - см. ниже
    author = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    # class Meta - также как в forms - задаём класс модели, из которой берём данные
    # и какие поля отдавать в json на выдачу
    class Meta:
        model = models.Post
        fields = [
            'title',
            'content',
            'date_posted',
            'author',
        ]

    # А поле author мы хотим отдать чуть по-другому. По умолчанию в json будет просто id автора поста.
    # А мы хотим его имя.
    #
    # Поэтому здесь мы определяем метод get_author (где get_ - зарезервированное соглашение)
    # а author - имя поля.

    # obj - это объект типа models.Post (мы задали это в class Meta) и этот объект мы собираемся вернуть в json

    # В итоге тут обращаемся к полю obj.author (тут работает ORM - поле author это объект типа User, потому что
    # мы задали ForeignKey в модели) и у этого user берём username.
    #
    # Но чтобы это работало (чтобы метод get_author вообще вызывался) мы должны явно сказать про это django.
    # Для этого выше стоит строчка author = serializers.SerializerMethodField() - т.е. поле author сериализуется
    # через метод класса.
    def get_author(self, obj):
        return obj.author.username

    # Для лучшего понимания - мы можем как хотим менять поля на выдачу.
    # Допустим мы хотим ещё отдать title поста только заглавными буквами.
    #
    # Важно: в этом случае поле становится read-only (в следующем примере есть про запрос PATCH,
    # так вот мы не сможем сделать PATCH на title, если title = serializers.SerializerMethodField())
    # По смыслу оно понятно - если внешнее представление не совпадает с внутренней фоормой хранения
    # то без явного указания как преобразовывать внешний вид данных по внутренний
    # django не знает как записывать это поле.
    # https://stackoverflow.com/questions/37475829/django-rest-framework-how-to-update-serializermethodfield
    def get_title(self, obj):
        return obj.title.upper()
