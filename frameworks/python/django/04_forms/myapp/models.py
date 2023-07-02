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
