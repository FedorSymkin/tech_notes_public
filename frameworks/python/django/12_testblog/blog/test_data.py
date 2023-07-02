"""
Здесь код для генерации общих тестовых данных, нужных как для юнит так и для интеграционных тестов
"""

import logging
from collections import defaultdict

from . import models


class TestData:
    def __init__(self):
        self.users = list()
        self.posts = defaultdict(list)
        self.subscribes = defaultdict(set)
        self.log = logging.getLogger('tests_functional')

    def mkuser(self, name, passwd=None):
        user = models.MyUser(username=name)
        user.set_password(passwd or name)
        user.save()
        self.log.debug('mkuser {}'.format(name))
        return user

    def mkusers(self, cnt):
        return [
            self.mkuser('user{}'.format(u), 'passwd{}'.format(u))
            for u in range(cnt)
        ]

    def mkpost(self, user, title, content):
        post = models.Post(
            user=user,
            title=title,
            content=content,
        )
        post.save()
        self.log.debug('mkpost {}'.format(title))
        return post

    def mkposts(self, user, start_num, cnt):
        return [
            self.mkpost(
                user,
                'post {} of {}'.format(n, user.username),
                'content {} of {}'.format(n, user.username),
            )
            for n in range(start_num, start_num + cnt)
        ]

    def mksubscribe(self, user, other):
        models.Subscribe(
            user_from=user,
            user_to=other,
        ).save()
        self.log.debug('mksubscribe {} to {}'.format(user, other))

    def mark_as_read(self, user, post):
        user.read_posts.add(post)
        self.log.debug('mark_as_read {} -> {}'.format(user, post))

    @property
    def users_count(self):
        return len(self.users)

    @property
    def posts_count(self):
        return sum([len(posts) for _, posts in self.posts.items()])

    @staticmethod
    def clean_all():
        models.MyUser.objects.all().delete()


class FunctionalTestData(TestData):
    def make_data(self):
        """
        Пользователь 2:
            * подписан на нескольких
            * несколько подписаны на него
            * часть постов до подписки, часть после
            * у него есть прочитанные посты

        Пользователь 1:
            * ни на кого не подписан
            * нет прочитанных постов
            * на него подписаны
            * его читали

        Пользователь 6:
            * никак не связан с другиеи пользовалетями
        """

        self.log.info('make_data')

        users_count = 7
        portion = 3

        self.users = self.mkusers(cnt=users_count)

        for n, user in enumerate(self.users):
            self.posts[n] += self.mkposts(user, start_num=0, cnt=portion)

        self.mksubscribe(self.users[2], self.users[4])
        self.mksubscribe(self.users[2], self.users[1])

        for n, user in enumerate(self.users):
            self.posts[n] += self.mkposts(user, start_num=portion, cnt=portion + n)

        self.mksubscribe(self.users[2], self.users[5])
        self.mksubscribe(self.users[4], self.users[2])
        self.mksubscribe(self.users[5], self.users[2])
        self.mksubscribe(self.users[3], self.users[2])
        self.mksubscribe(self.users[3], self.users[5])
        self.mksubscribe(self.users[5], self.users[1])

        self.mark_as_read(self.users[2], self.posts[1][1])
        self.mark_as_read(self.users[2], self.posts[4][7])
        self.mark_as_read(self.users[2], self.posts[4][8])
        self.mark_as_read(self.users[2], self.posts[1][4])
        self.mark_as_read(self.users[2], self.posts[5][1])
        self.mark_as_read(self.users[2], self.posts[5][4])
        self.mark_as_read(self.users[2], self.posts[3][3])

        self.mark_as_read(self.users[3], self.posts[5][4])
        self.mark_as_read(self.users[3], self.posts[5][5])
        self.mark_as_read(self.users[3], self.posts[2][3])
        self.mark_as_read(self.users[3], self.posts[2][4])


class PefomanceTestData(TestData):
    def __init__(self, create_users_count, create_post_portion, subscribes_per_user):
        super(PefomanceTestData, self).__init__()
        self.create_users_count = create_users_count
        self.create_post_portion = create_post_portion
        self.subscribes_per_user = subscribes_per_user

    def make_data(self):
        self.users = self.mkusers(cnt=self.create_users_count)

        for n, user in enumerate(self.users):
            self.posts[n] += self.mkposts(user, start_num=0, cnt=self.create_post_portion)

        # Считаем что каждый пользователь подписывается на subscribes_per_user следующих
        for i in range(len(self.users)):
            for j in range(self.subscribes_per_user):
                if j >= len(self.users):
                    break
                self.mksubscribe(self.users[i], self.users[j])

        for n, user in enumerate(self.users):
            self.posts[n] += self.mkposts(user, start_num=self.create_post_portion, cnt=self.create_post_portion)

        # Считаем что пользователи прочитали каждое 2-е сообщение
        for nuser in range(len(self.users)):
            for nother in self.subscribes[nuser]:
                for npost in range(0, len(self.posts[nother]), 2):
                    self.mark_as_read(self.users[nuser], self.posts[nother][npost])
