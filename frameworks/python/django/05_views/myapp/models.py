from django.db import models
from django.utils import timezone


# Тестовая модель данных, подробнее см раздел orm


class Department(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.TextField()
    join_date = models.DateTimeField(default=timezone.now)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.surname)


def make_default_data():
    # Сначала погрохать существующие данные, чтобы можно было несколько раз запускать
    Employee.objects.all().delete()
    Department.objects.all().delete()

    # Создаём объекты, соответствующие записям в таблице и сохраняем их в таблицу
    theoretical_physics = Department(name='theoretical_physics')
    experimental_physics = Department(name='experimental_physics')
    astro_physics = Department(name='astro_physics')
    engineers = Department(name='engineers')

    theoretical_physics.save()
    experimental_physics.save()
    astro_physics.save()
    engineers.save()

    sheldon = Employee(first_name='Sheldon', surname='Cooper', department=theoretical_physics)
    leonard = Employee(first_name='Leonard', surname='Hofstadter', department=experimental_physics)
    howard = Employee(first_name='Howard', surname='Wolowitz', department=engineers)
    raj = Employee(first_name='Raj', surname='Koothrappali', department=astro_physics)
    leslie = theoretical_physics.employee_set.create(first_name='Leslie', surname='Winkle')

    sheldon.save()
    leonard.save()
    howard.save()
    raj.save()
    leslie.save()
