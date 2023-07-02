from rest_framework import generics
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from . import serializers
from . import models
from .permissions import IsOwnerOrReadOnly


# Создаём пользователя через API. В текущем примере только создать, без возможности посмотреть список
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


# RetrieveUpdateDestroy View с ограничением доступа
class PostRUDView(generics.RetrieveUpdateDestroyAPIView):
    # Эти поля уже описаны в предыдущих примерах
    lookup_field = 'id'
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    # Вот так устанавливаются правила доступа. Здесь список из классов permission.
    # IsAuthenticated - это стандартный класс из rest_framework
    # IsOwnerOrReadOnly - это наш класс, см. permissions.py.
    # В результате по этим 2 правилам получится так, что залогиненные пользователи могут смотреть все сообщения
    # а править или удалять только свои
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class PostListView(generics.ListAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    # Просмотр списка сообщений - для всех залогиненных пользователей
    permission_classes = [IsAuthenticated]


class PostCreateView(generics.CreateAPIView):
    serializer_class = serializers.PostSerializer

    # Создание сообщения - для всех залогиненных пользователей
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # При создании поста, перехватываем создание чтобы назначить автора - см. предыдущие примеры
        serializer.save(author=self.request.user)
