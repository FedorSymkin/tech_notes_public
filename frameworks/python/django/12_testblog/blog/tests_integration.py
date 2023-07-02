import json

from django.test.testcases import LiveServerTestCase

from . import test_data


class DataChangeTestCase(LiveServerTestCase):
    def setUp(self):
        data = test_data.TestData()
        self.default_user = data.mkuser('default', 'somepasswd')

    def test_create_user(self):
        data_to_post = json.dumps({
            'username': 'user1',
            'password': 'passwd1',
        })

        def do_assert(response, code):
            self.assertEqual(response.status_code, code)
            self.assertEqual(response.data['username'], 'user1')
            self.assertEqual(response.data['posts_count'], 0)

        resp = self.client.post('/users/new/', content_type='application/json', data=data_to_post)
        do_assert(resp, 201)

        user_id = resp.data['id']

        resp = self.client.get('/users/{}/'.format(user_id))
        do_assert(resp, 200)

    def test_create_post(self):
        self.client.login(username='default', password='somepasswd')
        data_to_post = json.dumps({
            'title': 'some post of default user',
            'content': 'some content of default user',
        })

        def do_assert(response, code):
            self.assertEqual(response.status_code, code)
            self.assertEqual(response.data['username'], 'default')
            self.assertEqual(response.data['user'], self.default_user.id)
            self.assertEqual(response.data['title'], 'some post of default user')
            self.assertEqual(response.data['content'], 'some content of default user')
            self.assertTrue(bool(response.data['datetime']))

        resp = self.client.post('/me/posts/new/', content_type='application/json', data=data_to_post)
        do_assert(resp, 201)

        post_id = resp.data['id']

        resp = self.client.get('/posts/{}/'.format(post_id))
        do_assert(resp, 200)

    def test_create_subscribe(self):
        self.client.login(username='default', password='somepasswd')

        data = test_data.TestData()
        user2 = data.mkuser('user2')

        data_to_post = json.dumps({
            'user_to': user2.id,
        })

        def do_assert(response, code):
            self.assertEqual(response.status_code, code)
            self.assertEqual(response.data['user_from'], self.default_user.id)
            self.assertEqual(response.data['user_to'], user2.id)

        resp = self.client.post('/me/subscribes/new/', content_type='application/json', data=data_to_post)
        do_assert(resp, 201)

        resp = self.client.get('/me/subscribes/{}/'.format(user2.id))
        do_assert(resp, 200)

    def test_delete_subscribe(self):
        self.client.login(username='default', password='somepasswd')
        data = test_data.TestData()
        user2 = data.mkuser('user2')
        data.mksubscribe(self.default_user, user2)
        self.assertEqual(self.client.get('/me/subscribes/{}/'.format(user2.id)).status_code, 200)

        resp = self.client.delete('/me/subscribes/{}/'.format(user2.id))
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.client.get('/me/subscribes/{}/'.format(user2.id)).status_code, 404)

    def test_mark_as_read(self):
        data = test_data.TestData()
        user2 = data.mkuser('user2')
        post2 = data.mkpost(user2, 'some post of user2', 'some content of user2')

        self.client.login(username='default', password='somepasswd')
        resp = self.client.post('/posts/{}/mark_as_read/'.format(post2.id), data=None)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['user'], self.default_user.id)
        self.assertEqual(resp.data['post'], post2.id)


class DataRetrieveTestCase(LiveServerTestCase):
    def setUp(self):
        self.test_data = test_data.FunctionalTestData()
        self.test_data.make_data()

    def test_get_users(self):
        resp = self.client.get('/users/')
        self.assertEqual(resp.status_code, 200)

        expected = [
            {
                'username': 'user6',
                'posts_count': 12,
            },
            {
                'username': 'user5',
                'posts_count': 11,
            },
            {
                'username': 'user4',
                'posts_count': 10,
            },
            {
                'username': 'user3',
                'posts_count': 9,
            },
            {
                'username': 'user2',
                'posts_count': 8,
            },
            {
                'username': 'user1',
                'posts_count': 7,
            },
            {
                'username': 'user0',
                'posts_count': 6,
            },
        ]

        fact = [
            {
                'username': item.get('username'),
                'posts_count': item.get('posts_count'),
            }
            for item in resp.data['results']
        ]

        self.assertEqual(fact, expected)

    def _assert_user_posts(self, user_id, cnt, resp):
        expected = [
            {
                'title': 'post {} of user2'.format(n),
                'content': 'content {} of user2'.format(n),
                'user': user_id,
                'username': 'user2',
            }
            for n in reversed(range(cnt))
            ]

        fact = [
            {
                'title': item.get('title'),
                'content': item.get('content'),
                'user': item.get('user'),
                'username': item.get('username'),
            }
            for item in resp.data['results']
            ]

        self.assertEqual(fact, expected)

    def test_get_user_posts(self):
        user2_id = self.test_data.users[2].id
        resp = self.client.get('/users/{}/posts/'.format(user2_id))
        self.assertEqual(resp.status_code, 200)
        self._assert_user_posts(user2_id, 8, resp)

    def test_get_my_posts(self):
        user2_id = self.test_data.users[2].id
        self.client.login(username='user2', password='passwd2')
        resp = self.client.get('/me/posts/')
        self.assertEqual(resp.status_code, 200)
        self._assert_user_posts(user2_id, 8, resp)

    def test_feed(self):
        self.client.login(username='user2', password='passwd2')
        resp = self.client.get('/me/feed/')
        self.assertEqual(resp.status_code, 200)

        expected = [
            {
                'title': 'post 9 of user4',
            },
            # 7 и 8 - прочитаны
            {
                'title': 'post 6 of user4',
            },
            {
                'title': 'post 5 of user4',
            },
            {
                'title': 'post 4 of user4',
            },
            {
                'title': 'post 3 of user4',
            },
            # 0, 1, 2 созданы ранее, чем подписка

            {
                'title': 'post 6 of user1',
            },
            {
                'title': 'post 5 of user1',
            },
            # 4 - прочитан
            {
                'title': 'post 3 of user1',
            }

            # 0, 1, 2 созданы ранее, чем подписка
        ]

        fact = [
            {
                'title': item.get('title'),
            }
            for item in resp.data['results']
        ]

        self.assertEqual(fact, expected)

    def test_feed_no_posts(self):
        self.client.login(username='user6', password='passwd6')
        resp = self.client.get('/me/feed/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_get_subscribes(self):
        self.client.login(username='user2', password='passwd2')
        resp = self.client.get('/me/subscribes/')
        self.assertEqual(resp.status_code, 200)

        expected = [
            {
                'user_from': self.test_data.users[2].id,
                'user_to': self.test_data.users[4].id,
            },
            {
                'user_from': self.test_data.users[2].id,
                'user_to': self.test_data.users[1].id,
            },
            {
                'user_from': self.test_data.users[2].id,
                'user_to': self.test_data.users[5].id,
            },
        ]

        fact = [
            {
                'user_from': item.get('user_from'),
                'user_to': item.get('user_to'),
            }
            for item in resp.data['results']
        ]

        self.assertEqual(fact, expected)


class BadRequestTestCase(LiveServerTestCase):
    def setUp(self):
        data = test_data.TestData()
        self.default_user = data.mkuser('default', 'somepasswd')

    def test_get_non_existing_user(self):
        resp = self.client.get('/users/42/')
        self.assertEqual(resp.status_code, 404)

    def test_get_non_existing_post(self):
        resp = self.client.get('/posts/42/')
        self.assertEqual(resp.status_code, 404)

    def test_get_non_existing_user_posts(self):
        resp = self.client.get('/users/42/posts/')
        self.assertEqual(resp.status_code, 404)

    def test_subscribe_to_non_existing(self):
        self.client.login(username='default', password='somepasswd')

        data_to_post = json.dumps({
            'user_to': 42,
        })

        resp = self.client.post('/me/subscribes/new/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 400)

    def test_subscribe_duplicate(self):
        self.client.login(username='default', password='somepasswd')
        data = test_data.TestData()
        user2 = data.mkuser('user2')

        data_to_post = json.dumps({
            'user_to': user2.id,
        })
        resp = self.client.post('/me/subscribes/new/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post('/me/subscribes/new/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 400)

    def test_subscribe_to_self(self):
        self.client.login(username='default', password='somepasswd')
        data_to_post = json.dumps({
            'user_to': self.default_user.id,
        })
        resp = self.client.post('/me/subscribes/new/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 400)

    def test_read_post_non_existing(self):
        self.client.login(username='default', password='somepasswd')
        resp = self.client.post('/posts/42/make_as_read/')
        self.assertEqual(resp.status_code, 404)

    def test_read_post_duplicate(self):
        self.client.login(username='default', password='somepasswd')
        resp = self.client.post('/posts/42/make_as_read/')
        self.assertEqual(resp.status_code, 404)

    # Можно ещё тест на mark as read self post написать


class AuthentificationTestCase(LiveServerTestCase):
    def setUp(self):
        data = test_data.TestData()
        self.default_user = data.mkuser('default', 'somepasswd')

    def _get_token_default_user(self):
        data_to_post = json.dumps({
            'username': 'default',
            'password': 'somepasswd',
        })
        resp = self.client.post('/get_token/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 200)
        return resp.data['token']

    def test_auth_token(self):
        token = self._get_token_default_user()

        data_to_post = json.dumps({
            'title': 'some post of default user',
            'content': 'some content of default user',
        })

        resp = self.client.post(
            '/me/posts/new/',
            content_type='application/json',
            data=data_to_post,
            HTTP_AUTHORIZATION='Token {}'.format(token),
        )
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get('/users/{}/posts/'.format(self.default_user.id))
        self.assertEqual(resp.status_code, 200)

        expected = [
            {
                'title': 'some post of default user',
                'content': 'some content of default user',
                'username': 'default',
            }
        ]

        fact = [
            {
                'title': item.get('title'),
                'content': item.get('content'),
                'username': item.get('username'),
            }
            for item in resp.data['results']
        ]

        self.assertEqual(fact, expected)

    def test_get_token_invalid_password(self):
        data_to_post = json.dumps({
            'username': 'default',
            'password': 'badpasswd',
        })
        resp = self.client.post('/get_token/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('token' not in resp.data)

    def test_get_token_non_existing_user(self):
        data_to_post = json.dumps({
            'username': 'baduser',
            'password': 'badpasswd',
        })
        resp = self.client.post('/get_token/', content_type='application/json', data=data_to_post)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('token' not in resp.data)

    def test_invalid_token(self):
        data_to_post = json.dumps({
            'title': 'some post of default user',
            'content': 'some content of default user',
        })

        resp = self.client.post(
            '/me/posts/new/',
            content_type='application/json',
            data=data_to_post,
            HTTP_AUTHORIZATION='Token aaa',
        )

        self.assertEqual(resp.status_code, 401)

    def test_get_no_auth(self):
        data_to_post = json.dumps({
            'title': 'some post of default user',
            'content': 'some content of default user',
        })

        resp = self.client.post(
            '/me/posts/new/',
            content_type='application/json',
            data=data_to_post,
        )

        self.assertEqual(resp.status_code, 401)


class PaginationTestCase(LiveServerTestCase):
    def setUp(self):
        data = test_data.TestData()
        user = data.mkuser('default')
        for i in range(35):
            data.mkpost(user, 'post{}'.format(i), 'content')

    def _do_test(self, expected_range, page=None):
        url = '/posts/'
        if page:
            url += '?page={}'.format(page)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        expected = {
            'results': [{'title': 'post{}'.format(i)} for i in expected_range],
            'count': 35,
        }

        fact = {
            'results': [{'title': item.get('title')} for item in resp.data['results']],
            'count': resp.data['count'],
        }

        self.assertEqual(fact, expected)

    def test_first_page(self):
        self._do_test(expected_range=reversed(range(25, 35)))

    def test_second_page(self):
        self._do_test(expected_range=reversed(range(15, 25)), page=2)

    def test_last_page(self):
        self._do_test(expected_range=reversed(range(0, 5)), page=4)

    def test_non_existing_page(self):
        resp = self.client.get('/posts/?page=999')
        self.assertEqual(resp.status_code, 404)
