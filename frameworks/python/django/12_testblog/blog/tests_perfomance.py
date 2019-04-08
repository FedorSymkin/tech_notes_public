import logging
import time

from django.test.testcases import LiveServerTestCase

from . import test_data


class PerfomanceTestCase(LiveServerTestCase):
    def setUp(self):
        self.log = logging.getLogger('tests_perfomance')

    def _do_test(self, create_users_count, create_post_portion, subscribes_per_user):
        self.log.info('===============')
        self.log.info('TEST create_users_count={} create_post_portion={} subscribes_per_user={}'.format(
            create_users_count,
            create_post_portion,
            subscribes_per_user
        ))
        data = test_data.PefomanceTestData(create_users_count, create_post_portion, subscribes_per_user)

        self.log.info('make data for perfomance test...')
        data.make_data()
        self.log.info('OK, total users = {}, total posts = {}'.format(data.users_count, data.posts_count))

        self.client.login(username='user2', password='passwd2')

        self.log.info('start perfomance test (feed request)...')
        start = time.time()
        resp = self.client.get('/me/feed/')
        end = time.time()
        elapsed = end - start

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) > 0)

        self.log.info('OK, returned posts count: {}, request time = {}'.format(len(resp.data), elapsed))

        data.clean_all()
        return elapsed

    def test_feed_perfomance(self):
        little_data_time = self._do_test(
            create_users_count=10,
            create_post_portion=3,
            subscribes_per_user=2,
        )

        big_data_time = self._do_test(
            create_users_count=100,
            create_post_portion=10,
            subscribes_per_user=10,
        )

        diff = big_data_time / little_data_time if little_data_time else 'INF'
        self.log.info('time difference: {} times'.format(diff))

        self.assertTrue(big_data_time < 0.1)
        self.assertTrue(diff < 5.0)
