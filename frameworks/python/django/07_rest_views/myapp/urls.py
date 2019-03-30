from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('make_data', views.make_data, name='make_data'),

    # Здесь API view вызываетс также как и обычный view.
    # url - например /post/22. Переменную, которая 22,
    # назвали id, и потом к ней будем по этому имени обращаться в классе view
    path('post/<int:id>', views.PostView.as_view(), name='viewpost'),
]

