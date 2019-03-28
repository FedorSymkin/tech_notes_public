from django.contrib import admin
from .models import Employee, Department

# Register your models here.

# Регистрируем наши модели в админке, чтобы наслаждаться тем,
# как круто править свою БД прямо из админки. Нет, правда, это очень круто!
admin.site.register(Employee)
admin.site.register(Department)
