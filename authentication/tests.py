import json
from django.test import TestCase
from rest_framework import status

from authentication.models import User


class AuthenticationViewSetTestCase(TestCase):

    user_password = "1234bB1$"
    user_email = "abdelrahman.farag114@gmail.com"

    def verify_email_helper(self):

        user = {
            "name": "abdu",
            "email": self.user_email,
            "password": self.user_password
        }

        self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )

        userObject = User.objects.get(email=self.user_email)
        verify_token = userObject.verify_token

        verify_response = self.client.post('/api/verify_token', json.dumps({
            "verify_token": verify_token}), format="json", content_type="application/json")

        return {'verify_response': verify_response, 'user': user}

    # test creating user
    def test_creating_user(self):
        response = self.client.post('/api/users', json.dumps({
            "name": "abdu",
            "email": "abdelrahman.farag91@gmail.com",
            "password": self.user_password
        }), format="json", content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['access_tokens']['refresh'])
        self.assertIsNotNone(response.json()['access_tokens']['access'])

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

    def test_check_email_before_login(self):
        # test non existing user
        non_existing_user = {
            "email": "test@test.com"
        }

        api_response = self.client.post('/api/check_email_before_login',
                                        json.dumps(non_existing_user), format="json", content_type="application/json")

        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(api_response.content, encoding='utf8'),
            {'status': 1}
        )

        # check response for non verified user
        non_verified_user = {
            "email": "test@test.com"
        }

        self.client.post('/api/users', json.dumps({
            "name": "abdu",
            "email": "test@test.com",
            "password": self.user_password
        }), format="json", content_type="application/json")

        api_response = self.client.post('/api/check_email_before_login',
                                        json.dumps(non_verified_user), format="json", content_type="application/json")

        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(api_response.content, encoding='utf8'),
            {'status': 2}
        )

        # check response for verified user
        userObject = User.objects.get(email="test@test.com")
        verify_token = userObject.verify_token

        self.client.post('/api/verify_token', json.dumps({
            "verify_token": verify_token,
            "password": self.user_password}), format="json", content_type="application/json")

        api_response = self.client.post('/api/check_email_before_login',
                                        json.dumps(non_verified_user), format="json", content_type="application/json")

        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(api_response.content, encoding='utf8'),
            {'status': 3}
        )

    def test_resend_verification_email(self):

        user = {
            "name": "abdu",
            "email": self.user_email,
            "password": self.user_password
        }

        # create user
        self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )

        # request resend of verification email
        verify_response = self.client.post('/api/resend_verification_email', json.dumps({
            "email": self.user_email}), format="json", content_type="application/json")

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(verify_response.content, encoding='utf8'),
            {'status': 2}
        )

        userObject = User.objects.get(email=self.user_email)
        verify_token = userObject.verify_token
        self.client.post('/api/verify_token', json.dumps({
            "verify_token": verify_token}), format="json", content_type="application/json")

        verify_response = self.client.post('/api/resend_verification_email', json.dumps({
            "email": self.user_email}), format="json", content_type="application/json")

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(verify_response.content, encoding='utf8'),
            {'status': 1}
        )

        # request send verification email for non existing user
        verify_response = self.client.post('/api/resend_verification_email', json.dumps({
            "email": "non_exist@gmail.com"}), format="json", content_type="application/json")

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(verify_response.content, encoding='utf8'),
            {'status': 3}
        )

    def test_forgot_password(self):
        user = {
            "name": "abdu",
            "email": self.user_email,
            "password": self.user_password
        }
        # create user
        self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )
        # request forgot password
        verify_response = self.client.post('/api/forgot_password', json.dumps({
            "email": self.user_email}), format="json", content_type="application/json")
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_reset_password_with_wrong_input(self):
        user = {
            "name": "abdu",
            "email": self.user_email,
            "password": self.user_password
        }
        # create user
        self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )
        # request forgot password
        self.client.post('/api/forgot_password', json.dumps({
            "email": self.user_email}), format="json", content_type="application/json")
        user = User.objects.get(email=self.user_email)
        # request reset password
        reset_password_response = self.client.post('/api/reset_password', json.dumps({
            "reset_token": user.verify_token,
            "password": self.user_password, "confirm_password": "non_matching_password"}), format="json", content_type="application/json")
        self.assertEqual(reset_password_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_correct_input(self):
        user = {
            "name": "abdu",
            "email": self.user_email,
            "password": self.user_password
        }
        # create user
        self.client.post(
            '/api/users', json.dumps(user), format="json", content_type="application/json"
        )
        # request forgot password
        self.client.post('/api/forgot_password', json.dumps({
            "email": self.user_email}), format="json", content_type="application/json")
        user = User.objects.get(email=self.user_email)
        # request reset password
        reset_password_response = self.client.post('/api/reset_password', json.dumps({
            "reset_token": user.verify_token,
            "password": self.user_password, "confirm_password": self.user_password}), format="json", content_type="application/json")
        self.assertEqual(reset_password_response.status_code, status.HTTP_200_OK)
