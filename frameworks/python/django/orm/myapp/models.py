from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


"""
Здесь определяются модели. Под моделью понимается одновреенно класс питона и
саязанная с ним таблица в БД.
Здесь показан пример отношения многое-к-одному. Всё интуитивно понятно и похоже на sqlalchemy
(см. отдельный раздел про sqlalchemy)
"""


class Department(models.Model):
    name = models.TextField()


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.TextField()

    # Здесь важная штука - в default передаётся функция timezone.now, которая
    # вызывается при отсутствии значения
    join_date = models.DateTimeField(default=timezone.now)

    # Здесь мы привязываем внешний ключ - таблицу Department (образуется поле department_id)
    # on_delete=models.CASCADE - это вообще говоря фича SQL, а не django, но здесь django
    # будет сам эмулировать эту фичу. Смысл такой: при удалении записи из таблицы department
    # Происходит каскадное удаление всех записей из таблицы employee, завязанных на этот department
    # Таким образом, целостность данных не нарушается
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.surname)


@receiver(post_save, sender=Employee)
def save_profile(sender, instance, **kwargs):
    # Django умеет перехватывать события при работе с БД. Здесь просто пишем в консоль,
    # но на практике здесь можно параллельно что-нибудь ещё создать / изменить в БД
    print('saved: {}'.format(instance))
