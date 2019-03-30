from rest_framework import serializers
from . import models


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        fields = [
            # по сравнению с прошлым примером тут добавилось id, чтобы после создания
            # можно было руками посмотреть только что созданный post
            'id',

            'title',
            'content',
            'date_posted',
            'author',
        ]

    def get_author(self, obj):
        return obj.author.username

    def validate_title(self, value):
        # Проверяем поля перед записью. validate_... - зарерервированное название функции проверки
        if 'badword' in value:
            raise serializers.ValidationError("Title contains a bad word! Be more politely, man!")
        return value
