from django import forms
from . import models


# Здесь описываются классы форм


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        # Привязываем форму к модели БД - пишем саму модель и поля которые можно вводить
        model = models.Department
        fields = ['name']


class EmployeeCreateForm(forms.ModelForm):
    # А это пример доп. поля: email нет в Employee, но его также можно ввести и потом вручную получить
    email = forms.EmailField()

    class Meta:
        model = models.Employee

        # Здесь интересный момент - поскольку в модели данных есть связь между отделом и сотрудниками,
        # поле department будет показано в виде списка в опциями - выбрать из существующих отделов
        fields = ['first_name', 'surname', 'department']
