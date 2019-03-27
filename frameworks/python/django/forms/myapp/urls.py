from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_department', views.create_department, name='dep'),
    path('create_employee', views.create_employee, name='emp'),
]
