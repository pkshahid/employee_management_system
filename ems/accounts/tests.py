from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import TestCase, Client
from django.urls import reverse


class AuthAPITestCase(APITestCase):

    def setUp(self):
        """Setup test user"""

        self.user = User.objects.create_user(username="testuser", password="password123")
        self.token = RefreshToken.for_user(self.user)

    def test_login(self):
        """
        Test user login and token retrieval
        - Call the login endpoint with valid user credntials
        - Check the response code is 200.
        - Check the response has access token.
        - Check the response has refresh token

        - Call the login endpoint with invalid credntials.
        - Check the response code is 400
        """

        # Positive case
        response = self.client.post('/api/token/',{
            "username": "testuser", "password": "password123"
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        response = self.client.post('/api/token/', {
            "username": "", "password": "password123"
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token(self):
        """
        Test token refresh
        - Call token refresh endpoint with a valid refresh token
        - Check the response code is 200
        - Check the response has access token
        - Check the response has refresh token

        - Call the token refresh endpoint with invalid refresh token
        - Check the response code is 401
        """

        # Positve case
        response = self.client.post('/api/token/refresh/', {
            "refresh": str(self.token)
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        # Negative case
        response = self.client.post('/api/token/refresh/', {
            "refresh": "abc21441"
            }, format='json')
            
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




class AccountViewsTestCase(TestCase):
    '''
    Setup
    '''

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.password_change_url = reverse('password_change')

        self.user_data = {
            'username': 'testuser',
            'password1': 'Str0ngPass123!',
            'password2': 'Str0ngPass123!'
        }

    def test_register_view_get(self):
        """
        Test to render the register page
        """

        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_view_post_valid(self):
        """
        Test to successfull registration.
        """
        
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_post_invalid(self):
        """
        Test to invalid registration.
        """

        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'wrongpass'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")

    def test_login_view_get(self):
        """
        Test login page rendering.
        """

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_and_profile_access(self):
        """
        Test to successful login redirects to profile page.
        """
        user = User.objects.create_user(username='user1', password='Str0ngPass123!')
        login = self.client.login(username='user1', password='Str0ngPass123!')
        self.assertTrue(login)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_requires_login(self):
        """
        Test to login_required permission to profile page.
        """
         
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_logout_redirects_to_login(self):
        """
        Test logout redirection.
        """

        user = User.objects.create_user(username='user2', password='Str0ngPass123!')
        self.client.login(username='user2', password='Str0ngPass123!')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
