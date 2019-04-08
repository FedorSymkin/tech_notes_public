from django.contrib import admin
from . import models

admin.site.register(models.MyUser)
admin.site.register(models.Post)
admin.site.register(models.Subscribe)
admin.site.register(models.MyUser.read_posts.through)
