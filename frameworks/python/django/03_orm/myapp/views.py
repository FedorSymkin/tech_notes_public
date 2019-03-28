from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import escape
from . import models

# Create your views here.


def make_data():
    # Сначала погрохать существующие данные, чтобы можно было несколько раз запускать
    models.Employee.objects.all().delete()
    models.Department.objects.all().delete()

    # Создаём объекты, соответствующие записям в таблице и сохраняем их в таблицу
    theoretical_physics = models.Department(name='theoretical_physics')
    experimental_physics = models.Department(name='experimental_physics')
    astro_physics = models.Department(name='astro_physics')
    engineers = models.Department(name='engineers')

    theoretical_physics.save()
    experimental_physics.save()
    astro_physics.save()
    engineers.save()

    # Вот так выглядит привязка многого в одному
    sheldon = models.Employee(first_name='Sheldon', surname='Cooper', department=theoretical_physics)
    leonard = models.Employee(first_name='Leonard', surname='Hofstadter', department=experimental_physics)
    howard = models.Employee(first_name='Howard', surname='Wolowitz', department=engineers)
    raj = models.Employee(first_name='Raj', surname='Koothrappali', department=astro_physics)
    # А здесь ещё один способ привязки - через объект из таблицы departments
    leslie = theoretical_physics.employee_set.create(first_name='Leslie', surname='Winkle')

    sheldon.save()
    leonard.save()
    howard.save()
    raj.save()
    leslie.save()


def test_reqs():
    # Примеры того, как вытаскиваются данные из БД

    res = dict()
    res['all_people'] = models.Employee.objects.all()

    # Здесь тип данных будет QuerySet
    res['sheldon'] = models.Employee.objects.filter(surname='Cooper')

    # А здесь тип просто Employee
    res['sheldon_single'] = models.Employee.objects.filter(surname='Cooper').first()

    theoretical_physics = models.Department.objects.filter(name='theoretical_physics').first()
    if theoretical_physics:
        res['theoretical_physics_people'] = theoretical_physics.employee_set.all()
    else:
        res['theoretical_physics_people'] = 'no department'
    return res


def delete_department():
    # Здесь важная штука демонстрируется:
    # При создании таблиц у нас было указано on_delete=CASCADE,
    # и это значит что при удалении theoretical_physics у нас удалится Шелдон и Лесли автоматически.
    models.Department.objects.filter(name='theoretical_physics').delete()


def ormtest(request):
    make_data()
    res = ''

    data = test_reqs()
    res += '<h2>first stage (data added)</h2>'
    res += '<br>'.join(['{}: {}'.format(k, escape(v)) for k, v in data.items()])

    delete_department()

    data = test_reqs()
    res += '<h2>second stage (department deleted)</h2>'
    res += '<br>'.join(['{}: {}'.format(k, escape(v)) for k, v in data.items()])

    return HttpResponse(res)
