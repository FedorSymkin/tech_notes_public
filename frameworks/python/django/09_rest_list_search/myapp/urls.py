from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('make_data', views.make_data, name='make_data'),

    path('posts', views.PostListSearchView.as_view(), name='posts'),
]
