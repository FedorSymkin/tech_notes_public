from django.contrib.auth import views as std_auth_views
from django.urls import path
from rest_framework.authtoken import views as api_auth_views
from rest_framework.documentation import include_docs_urls

from . import views
from .feed_view import FeedView


# см. описание урлов в README, секция API URLs, short description
urlpatterns = [
    # public
    path('users/', views.UserListView.as_view()),
    path('users/new/', views.UserCreateView.as_view()),
    path('users/<int:id>/', views.UserDetailsView.as_view()),
    path('users/<int:id>/posts/', views.UserPostsView.as_view()),
    path('posts/', views.PostListView.as_view()),
    path('posts/<int:id>/', views.PostDetailsView.as_view()),

    # need auth
    path('me/posts/new/', views.CreatePostView.as_view()),
    path('me/posts/', views.MyPostsView.as_view()),
    path('me/subscribes/new/', views.CreateSubscribeView().as_view()),
    path('me/subscribes/', views.MySubscribesView.as_view()),
    path('me/subscribes/<int:user_to_id>/', views.MySubscribeRDView.as_view()),
    path('me/feed/', FeedView.as_view()),
    path('posts/<int:id>/mark_as_read/', views.MarkAsReadView.as_view()),

    # login & logout
    path('login/', std_auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', std_auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('get_token/', api_auth_views.obtain_auth_token, name='get_token'),

    # docs
    path('', include_docs_urls(title='Simple Blog API')),
]
