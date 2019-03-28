# coding=utf-8

from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home),
    path('restapi/<slug:strval>/<int:intval>/', views.restapi, name='restapi'),

    # re_path is new in django 2.0 https://docs.djangoproject.com/en/2.1/ref/urls/#re-path
    re_path(r'regexp.*end', views.regexp, name='regexp'),

    path('get_params', views.get_params, name='get_params'),
    path('methods', views.methods, name='methods'),

    path('redirect', views.redir_src, name='redir-src'),
    path('redirected', views.redir_dest, name='redir-dest'),
    path('headers/<slug:header_name>', views.headers_example, name='headers'),

    path('cookie', views.cookie_exapmle, name='cookie'),

    path('bad_request', views.bad_request, name='bad'),
]
