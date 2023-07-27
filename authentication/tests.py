import json
from django.test import TestCase
from rest_framework import status


class AuthenticationViewSetTestCase(TestCase):

    user_password = "1234bB1$"

    def verify_email_helper(self):

        user = {
            "name": "abdu",
            "email": "abdelrahman.farag114@gmail.com"
        }

        response = self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )

        verify_token = json.loads(
            response.content.decode('utf-8'))['verify_token']

        verify_response = self.client.post('/api/verify_token', json.dumps({
            "verify_token": verify_token,
            "password": self.user_password}), format="json", content_type="application/json")

        return {'verify_response': verify_response, 'user': user}

    # test creating user
    def test_creating_user(self):
        response = self.client.post('/api/users', json.dumps({
            "name": "abdu",
            "email": "abdelrahman.farag91@gmail.com",
        }), format="json", content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # test login user

    def test_login(self):
        verify_response = self.verify_email_helper()

        # get user object from verify_email_helper()
        user = verify_response['user']

        # login with user email, and user password
        login_response = self.client.post('/api/login', json.dumps({
            "email": user['email'],
            "password": self.user_password}), format="json", content_type="application/json")

        # assert result status code is 200, response has access, refresh tokens, and user object
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(login_response.data['refresh'])
        self.assertIsNotNone(login_response.data['access'])
        self.assertIsNotNone(login_response.data['user'])
