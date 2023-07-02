from django.urls import path
from . import views as my_views
from rest_framework.authtoken import views as api_auth_views


urlpatterns = [
    path('register', my_views.CreateUserView.as_view(), name='register'),
    path('get_token', api_auth_views.obtain_auth_token, name='get_token'),

    path('posts', my_views.PostListView.as_view(), name='posts_list'),
    path('posts/<int:id>', my_views.PostRUDView.as_view(), name='post'),
    path('posts/new', my_views.PostCreateView.as_view(), name='post_new'),
]
