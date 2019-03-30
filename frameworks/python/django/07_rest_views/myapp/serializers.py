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

    # Для лучшего понимания - мы можем как хотим менят поля на выдачу.
    # Допустим мы хотим ещё отдать title поста только заглавными буквами
    def get_title(self, obj):
        return obj.title.upper()
