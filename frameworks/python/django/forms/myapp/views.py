from django.shortcuts import render, redirect
from django.urls import reverse
from . import forms
from django.http import HttpResponse, HttpResponseBadRequest


# Делаем 2 формы - создать отдел и создать сотрудника


def home(request):
    return HttpResponse('''
        <a href='{}'>create department</a><br/>
        <a href='{}'>create employee</a><br/>
        <a href='{}'>admin</a>
    '''.format(
        reverse('dep'),
        reverse('emp'),
        '/admin'
    ))


def create_department(request):
    if request.method == 'POST':

        # создаём объект формы и передаём ему POST данные которые дал пользователь
        # в данном случае объект формы выступает как писатель в БД.
        form = forms.DepartmentCreateForm(request.POST)
        if form.is_valid():
            form.save()  # тут пишем в БД

            return redirect('home')

        else:
            return HttpResponseBadRequest('invalid')

    else:
        # А здесь создаём объект формы в качестве формирователя html-формы.
        # Передаём форму как параметр в html шаблон
        form = forms.DepartmentCreateForm()
        return render(request, 'test.html', {'form': form, 'title': 'create department'})


def create_employee(request):
    if request.method == 'POST':

        # Здесь пишем email в консоль, чтобы показать, что у формы есть дополнительное поле,
        # которое не попадает в базу (потому что нет такой колонки), но его можно получить руками
        print(request.POST['email'])

        form = forms.EmployeeCreateForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('home')

        else:
            return HttpResponseBadRequest('invalid')

    else:
        form = forms.EmployeeCreateForm()
        return render(request, 'test.html', {'form': form, 'title': 'create employee'})
