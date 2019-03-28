from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as my_views

urlpatterns = [
    path('', my_views.home),
    path('who_am_i', my_views.who_am_i, name='who_am_i'),

    path('blog', my_views.AllPostsView.as_view(), name='blog'),
    path('blog/new_post', my_views.NewPostView.as_view(), name='new_post'),
    path('blog/update_post/<int:pk>/', my_views.UpdatePostView.as_view(), name='update_post'),

    path('register/', my_views.register, name='register'),

    # заметим что view для логина и логаута используются стандартные джанговские
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
]
