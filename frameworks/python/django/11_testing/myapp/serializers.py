from rest_framework import serializers
from django.contrib.auth.models import User
from . import models


class PostSerializer(serializers.ModelSerializer):
    # Описание PostSerializer уже было в одном из прошлых примеров
    author = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        fields = [
            'id',
            'title',
            'content',
            'date_posted',
            'author',
        ]

    def get_author(self, obj):
        return obj.author.username


class UserSerializer(serializers.ModelSerializer):
    # Делаем отдельный Serializer для стандартной модели пользователя django.
    # Это надо для того, чтобы создавать пользователя через API
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

        # password write_only, чтобы не показывать пароль (пусть даже захешированный) в ответе API
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, data):
        user = User.objects.create(
            username=data['username'],
        )

        # Безопасная установка пароля при создании пользователя
        user.set_password(data['password'])
        user.save()

        return user
