import json
from django.test import TestCase
from rest_framework import status


class AuthenticationViewSetTestCase(TestCase):

    # test creating user
    def test_creating_user(self):
        response = self.client.post('/api/users', json.dumps({
            "name": "abdu",
            "email": "abdelrahman.farag91@gmail.com",
        }), format="json", content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
