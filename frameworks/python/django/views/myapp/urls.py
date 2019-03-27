from django.urls import path
from . import views

# Видим, что здесь почти везде вместо просто функции обработчика стоит класс из молудя view
# (который унаследован из стандартного djando-вского view), и вызывается as_view(),
# которая возвращает сущность (объект, функцию, не важно), которая ведёт себя также как
# обработчик маршрута. И внутри этой сущности автоматизированы рутинные вещи.

urlpatterns = [
    # служебное
    path('', views.home, name='home'),
    path('make_data', views.make_data, name='make_data'),

    # общий список сотрудников
    path('employees', views.EmployeeListView.as_view(), name='employee_list'),

    # посмотреть конкретного сотрудника. Здесь используется запись, аналогичная примеру base в этом репозитории
    # int:pk - это значит что путь вида /employees/42/, где 42 - id сотрудника.
    # Важная вещь - значение названо pk, если бы мы сюда в обработчик ставили обычную функцию, она бы выглядела так:
    # def handler(pk)
    # это название pk (primary key) - зарезервировано внутри класса view. Класс пойдёт в БД за сотрудником с этим pk
    path('employees/<int:pk>/', views.EmployeeDetailsView.as_view(), name='employee_details'),

    path('employees/new/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
]
