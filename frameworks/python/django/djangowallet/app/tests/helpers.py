from django.test import TransactionTestCase
from django.test import LiveServerTestCase


class UnitTestCase(TransactionTestCase):
    fixtures = ['currencies.json']


class IntegrationTestCase(LiveServerTestCase):
    fixtures = ['currencies.json']
