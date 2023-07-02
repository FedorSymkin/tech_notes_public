from django.test import TestCase
from django.test.testcases import LiveServerTestCase
from django.contrib.auth.models import User
from .models import Post
from django.test import Client
import json


def _mkuser(name, passwd):
    # helper
    user = User(username=name)
    user.set_password(passwd)
    user.save()
    return user


def _mkpost(user, title, content):
    # helper
    Post.objects.create(
        author=user,
        title=title,
        content=content,
    )


# пример юнит-теста - проверяем внутренность программы - в данном случае добавление данных в модель.
# Тут даже вообще нет никакого API. Класс django.test.TestCase откуда наследуемся выполняет грязную
# работу по созданию фейковой базы и т.д.
class ModelsUnitTestCase(TestCase):
    def setUp(self):
        # Подготовка данных теста, запускается на каждый тест
        # Делаем 3 пользователя и каждому по 3 сообщения
        users = [_mkuser('user{}'.format(u), 'passwd{}'.format(u)) for u in range(3)]
        for user in users:
            for n in range(3):
                _mkpost(
                    user,
                    'post {} of {}'.format(n, user.username),
                    'content {} of {}'.format(n, user.username),
                )

    def test_posts_count(self):
        # пример юнит-теста. Можно придумать много кейсов, но здесь только общий смысл, поэтому только этот пример
        self.assertEqual(Post.objects.count(), 9)

    # def test_posts_count_bad(self):
    #    Этот тест упадёт AssertionError: 9 != 8
    #    self.assertEqual(Post.objects.count(), 8)


# Пример интеграционного теста - LiveServerTestCase обеспечивает запусе сервера целиком
class GetPostsIntegrationTestCase(LiveServerTestCase):
    def setUp(self):
        # Подготовка данных теста, запускается на каждый тест
        # Делаем 3 пользователя и каждому по 3 сообщения
        users = [_mkuser('user{}'.format(u), 'passwd{}'.format(u)) for u in range(3)]
        for user in users:
            for n in range(3):
                _mkpost(
                    user,
                    'post {} of {}'.format(n, user.username),
                    'content {} of {}'.format(n, user.username),
                )

        self.client = Client()

    def test_posts_count(self):
        # т.е. вот здесь уже имеем запущенный сервер на фейковой базе данных
        user_data = json.dumps({
            'username': 'user1',
            'password': 'passwd1',
        })

        # Получаем токен для уже готового пользователя которого создали в setUp
        token_resp = self.client.post('/api/get_token', content_type='application/json', data=user_data)
        self.assertEqual(token_resp.status_code, 200)
        token = token_resp.data['token']

        # используя этот токех получаем список постов блога
        posts_resp = self.client.get('/api/posts', HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(posts_resp.status_code, 200)
        self.assertEqual(len(posts_resp.data), 9)
