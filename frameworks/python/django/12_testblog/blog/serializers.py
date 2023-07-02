from rest_framework import serializers
from . import models


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    datetime = serializers.ReadOnlyField()

    class Meta:
        model = models.Post
        fields = (
            'id',
            'title',
            'content',
            'datetime',
            'user',
            'username',
        )

    @staticmethod
    def get_username(obj):
        return obj.user.username

    @staticmethod
    def get_user(obj):
        return obj.user.id


class MyUserSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = models.MyUser
        fields = ('id', 'username', 'password', 'posts_count')

        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, data):
        user = models.MyUser.objects.create(
            username=data['username'],
        )
        user.set_password(data['password'])
        user.save()
        return user

    @staticmethod
    def get_posts_count(obj):
        return getattr(obj, 'posts_count', 0)


class SubscribeSerializer(serializers.ModelSerializer):
    user_from = serializers.SerializerMethodField()

    class Meta:
        model = models.Subscribe
        fields = ('id', 'user_from', 'user_to')

    @staticmethod
    def get_user_from(obj):
        return obj.user_from.id


class MarkAsReadSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = models.MyUser.read_posts.through
        fields = ('user', 'post')

    @staticmethod
    def get_user(obj):
        return obj.myuser.id

    @staticmethod
    def get_post(obj):
        return obj.post.id
