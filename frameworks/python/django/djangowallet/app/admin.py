from django.contrib import admin
from . import models

admin.site.register(models.MyUser)
admin.site.register(models.Currency)
admin.site.register(models.Wallet)
admin.site.register(models.Operation)
admin.site.register(models.OperationStatus)
admin.site.register(models.StatusChange)
