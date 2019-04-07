from rest_framework import generics
from rest_framework import exceptions
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.http import Http404
from django.db import IntegrityError

from . import models
from . import serializers


class BadRequestException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class UserListView(generics.ListAPIView):
    serializer_class = serializers.MyUserSerializer
    queryset = models.MyUser.objects.all().annotate(posts_count=Count('post')).order_by('-posts_count')


class UserCreateView(generics.CreateAPIView):
    queryset = models.MyUser.objects.all()
    serializer_class = serializers.MyUserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = models.MyUser.objects.all()
    serializer_class = serializers.MyUserSerializer


class UserPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        userid = self.kwargs['userid']
        user = models.MyUser.objects.filter(id=userid).first()
        if not user:
            raise Http404('Not found.')
        return user.post_set.all().order_by('-datetime')


class PostDetailsView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = serializers.PostSerializer
    queryset = models.Post.objects.all()


class MyPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        userid = self.request.user.id
        return models.Post.objects.filter(user_id=userid).order_by('-datetime')


class CreatePostView(generics.CreateAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MarkAsReadView(generics.CreateAPIView):
    serializer_class = serializers.MarkAsReadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(myuser=self.request.user, post_id=post_id)


class MySubscribesView(generics.ListAPIView):
    serializer_class = serializers.SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        userid = self.request.user.id
        return models.Subsribe.objects.filter(user_from_id=userid)


class CreateSubscribeView(generics.CreateAPIView):
    queryset = models.Subsribe.objects.all()
    serializer_class = serializers.SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_to_id = self.request.data.get('user_to')
        user_from_id = self.request.user.id
        if user_to_id == user_from_id:
            raise BadRequestException('cannot subscribe to self')

        try:
            serializer.save(user_from=self.request.user)
        except IntegrityError as e:
            raise BadRequestException(str(e))


class MySubscribeRDView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.SubscribeSerializer
    lookup_field = 'user_to_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Subsribe.objects.filter(user_from_id=self.request.user.id)


class PostRetrieveView(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
