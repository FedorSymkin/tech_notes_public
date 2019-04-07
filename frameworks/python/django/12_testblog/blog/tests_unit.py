from django.test import TestCase
from django.db.utils import IntegrityError

from . import test_data
from . import models


class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data.FunctionalTestData().make_data()

    def test_user(self):
        user = models.MyUser.objects.get(username='user2')
        fact = str(user)
        expected = 'user2'
        self.assertEqual(fact, expected)

    def test_post(self):
        fact = str(models.Post.objects.get(title='post 2 of user0'))
        expected = 'post 2 of user0'
        self.assertEqual(fact, expected)

    def test_users_posts(self):
        user = models.MyUser.objects.get(username='user2')
        fact = str(user.post_set.first())
        expected = 'post 0 of user2'
        self.assertEqual(fact, expected)

    def test_posts_users(self):
        fact = str(models.Post.objects.get(title='post 2 of user0').user)
        expected = 'user0'
        self.assertEqual(fact, expected)

    def test_users_subscribes(self):
        user = models.MyUser.objects.get(username='user2')
        self.assertEqual(str(user.suserfrom.first()), 'Subscribe user2 to user4')
        self.assertEqual(str(user.suserto.first()), 'Subscribe user4 to user2')

    def test_users_read_posts(self):
        user = models.MyUser.objects.get(username='user2')
        fact = str(user.read_posts.first())
        expected = 'post 1 of user1'
        self.assertEqual(fact, expected)


class DuplicatesTestCase(TestCase):
    def test_subscribe_duplicate(self):
        data = test_data.FunctionalTestData()

        user1 = data.mkuser('user1')
        user2 = data.mkuser('user2')

        data.mksubscribe(user1, user2)
        with self.assertRaises(IntegrityError):
            data.mksubscribe(user1, user2)

    def test_read_post_duplicate(self):
        data = test_data.FunctionalTestData()

        user1 = data.mkuser('user1')
        user2 = data.mkuser('user2')
        user2post = data.mkpost(user2, 'post', 'data')

        data.mark_as_read(user1, user2post)
        data.mark_as_read(user1, user2post)

        self.assertEqual(len(user1.read_posts.through.objects.all()), 1)

    def test_username_duplicate(self):
        data = test_data.FunctionalTestData()
        data.mkuser('user1')

        with self.assertRaises(IntegrityError):
            data.mkuser('user1')


class CascaseDeleteTestCase(TestCase):
    def setUp(self):
        test_data.FunctionalTestData().make_data()

    def test_delete_user(self):
        user = models.MyUser.objects.get(username='user2')
        user_id = user.id

        self.assertNotEqual(len(models.MyUser.objects.filter(id=user_id)), 0)
        self.assertNotEqual(len(models.Post.objects.filter(user_id=user_id)), 0)
        self.assertNotEqual(len(models.Subsribe.objects.filter(user_from_id=user_id)), 0)
        self.assertNotEqual(len(models.Subsribe.objects.filter(user_to_id=user_id)), 0)
        self.assertNotEqual(len(models.MyUser.read_posts.through.objects.filter(myuser_id=user_id)), 0)

        user.delete()

        self.assertEqual(len(models.MyUser.objects.filter(id=user_id)), 0)
        self.assertEqual(len(models.Post.objects.filter(user_id=user_id)), 0)
        self.assertEqual(len(models.Subsribe.objects.filter(user_from_id=user_id)), 0)
        self.assertEqual(len(models.Subsribe.objects.filter(user_to_id=user_id)), 0)
        self.assertEqual(len(models.MyUser.read_posts.through.objects.filter(myuser_id=user_id)), 0)

    def test_delete_post(self):
        post = models.Post.objects.get(title='post 4 of user2')
        post_id = post.id

        self.assertNotEqual(len(models.MyUser.read_posts.through.objects.filter(post_id=post_id)), 0)

        post.delete()

        self.assertEqual(len(models.MyUser.read_posts.through.objects.filter(post_id=post_id)), 0)
