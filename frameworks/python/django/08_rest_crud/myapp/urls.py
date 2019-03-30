from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('make_data', views.make_data, name='make_data'),

    path('post/<int:id>', views.PostRUDView.as_view(), name='post_rud'),
    path('post/new', views.PostCreateView.as_view(), name='post_new'),
]
