import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from unittest.mock import patch
from .views import password_reset_confirm, get_user_by_uid, handle_post_request, redirect_to_confirm_page
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, EmailAuthTokenSerializer
from unittest.mock import patch
from .authentication import EmailBackend
from django.contrib.auth.backends import ModelBackend


base_url = 'http://localhost:4200/'
email_url = 'localhost:4200'
User = get_user_model()

class PasswordResetConfirmTests(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_get_user_by_uid_valid(self):
        user = get_user_by_uid(self.uidb64)
        self.assertEqual(user, self.user)

    def test_get_user_by_uid_invalid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(999))
        user = get_user_by_uid(uidb64)
        self.assertIsNone(user)

    def test_handle_post_request_valid(self):
        request = self.factory.post('/password-reset-confirm/', data=json.dumps({'new_password': 'newpassword123'}), content_type='application/json')
        response = handle_post_request(request, self.user)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Password has been reset successfully'})

    def test_handle_post_request_no_password(self):
        request = self.factory.post('/password-reset-confirm/', data=json.dumps({}), content_type='application/json')
        response = handle_post_request(request, self.user)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'New password is required'})

    def test_handle_post_request_invalid_data(self):
        request = self.factory.post('/password-reset-confirm/', data='invalid data', content_type='application/json')
        response = handle_post_request(request, self.user)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid request data'})

    def test_redirect_to_confirm_page(self):
        response = redirect_to_confirm_page(self.uidb64, self.token)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/password-reset-confirm/{self.uidb64}/{self.token}/", response.url)

    @patch('django.shortcuts.redirect')
    def test_password_reset_confirm_valid(self, mock_redirect):
        request = self.factory.get(f'/password-reset-confirm/{self.uidb64}/{self.token}/')
        response = password_reset_confirm(request, self.uidb64, self.token)
        mock_redirect.assert_called_with(f"{base_url}/password-reset-confirm/{self.uidb64}/{self.token}/")

    def test_password_reset_confirm_invalid_link(self):
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(999))
        request = self.factory.get(f'/password-reset-confirm/{invalid_uidb64}/{self.token}/')
        response = password_reset_confirm(request, invalid_uidb64, self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid link'})

    def test_password_reset_confirm_post_valid(self):
        request = self.factory.post(f'/password-reset-confirm/{self.uidb64}/{self.token}/', data=json.dumps({'new_password': 'newpassword123'}), content_type='application/json')
        response = password_reset_confirm(request, self.uidb64, self.token)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Password has been reset successfully'})

    def test_password_reset_confirm_post_invalid(self):
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(999))
        request = self.factory.post(f'/password-reset-confirm/{invalid_uidb64}/{self.token}/', data=json.dumps({'new_password': 'newpassword123'}), content_type='application/json')
        response = password_reset_confirm(request, invalid_uidb64, self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid link'})
        
class UserSerializerTests(TestCase):
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer_create(self):
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(User.objects.count(), 2)  # One existing user and one new user

    def test_user_serializer_create_missing_fields(self):
        invalid_data = self.user_data.copy()
        del invalid_data['email']
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class EmailAuthTokenSerializerTests(TestCase):
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_email_auth_token_serializer_valid(self):
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        serializer = EmailAuthTokenSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_email_auth_token_serializer_invalid_email(self):
        data = {
            'email': 'invalid@example.com',
            'password': self.user_data['password']
        }
        serializer = EmailAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(serializer.errors['non_field_errors'], ['User does not exist.'])

    def test_email_auth_token_serializer_invalid_password(self):
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        serializer = EmailAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(serializer.errors['non_field_errors'], ['Unable to log in with provided credentials.'])
        

class EmailBackendTests(TestCase):
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.backend = EmailBackend()

    def test_authenticate_with_valid_email_and_password(self):
        user = self.backend.authenticate(None, username=self.user_data['email'], password=self.user_data['password'])
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.user_data['email'])

    def test_authenticate_with_invalid_email(self):
        user = self.backend.authenticate(None, username='invalid@example.com', password=self.user_data['password'])
        self.assertIsNone(user)

    def test_authenticate_with_invalid_password(self):
        user = self.backend.authenticate(None, username=self.user_data['email'], password='wrongpassword')
        self.assertIsNone(user)

    def test_authenticate_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        user = self.backend.authenticate(None, username=self.user_data['email'], password=self.user_data['password'])
        self.assertIsNone(user)

    def test_get_user_with_valid_user_id(self):
        user = self.backend.get_user(self.user.pk)
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_get_user_with_invalid_user_id(self):
        user = self.backend.get_user(999)
        self.assertIsNone(user)