from rest_framework.test import APIClient
from django.test import TestCase


class ApiTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
