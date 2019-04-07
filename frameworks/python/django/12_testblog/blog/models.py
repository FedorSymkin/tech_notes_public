from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    read_posts = models.ManyToManyField('post', symmetrical=False)

    # Subsribe через ManyToManyField и through не стал делать, потому что иначе не рабоатет запрос в feed_view -
    # нам надо получить не Users по подпискам а сами подписки Subsribe, чтобы брать оттуда datetime


class Post(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    content = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Subsribe(models.Model):
    user_from = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='suserfrom')
    user_to = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='suserto')
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user_from', 'user_to', ), )

    def __str__(self):
        return 'Subscribe {} to {}'.format(self.user_from, self.user_to)
