from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    # В settings.py прописано, что использовать этот класс как модель для пользователей
    read_posts = models.ManyToManyField('post', symmetrical=False)

    # subscribes = models.ManyToManyField('self', symmetrical=False, through='subscribe')
    # Subscribe через ManyToManyField и through не стал делать, потому что иначе не рабоатет запрос в feed_view -
    # нам надо получить не Users по подпискам а сами подписки Subscribe, чтобы брать оттуда datetime


class Post(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    content = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Subscribe(models.Model):
    # related_name используется в запросах ORM и используется для join-а
    user_from = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='suserfrom')
    user_to = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='suserto')
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        # Делается уникальный индекс по этим полям в БД
        unique_together = (('user_from', 'user_to', ), )

    def __str__(self):
        return 'Subscribe {} to {}'.format(self.user_from, self.user_to)
