from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Здесь модель данных уже не про сотрудников, а про блог - так легче демонстрировать API


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


def make_data():
    # Делаем тестовые данные.

    # Сначала погрохать существующие данные, чтобы можно было несколько раз запускать
    # Грохаем всех пользователей, включая superuser - в этом примере админка не нужна
    Post.objects.all().delete()
    User.objects.all().delete()

    # Создаём пользователей
    petya = User.objects.create_user(username='petya',
                                     email='petya@example.com',
                                     password='petyapassword')

    vasya = User.objects.create_user(username='vasya',
                                     email='vasya@example.com',
                                     password='vasyapassword')
    petya.save()
    vasya.save()

    # Создаём посты - по 5 постов каждому юзеру
    def mkposts(user, count):
        res = [
            Post(
                title='Post {} of {}'.format(n, user.username),
                content='Data {} of {}'.format(n, user.username),
                author=user
            )
            for n in range(count)
        ]
        for post in res:
            post.save()
        return res

    mkposts(petya, 5)
    mkposts(vasya, 5)
