from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class AuthenticationTests(TestCase):
    """
    Testy rejestracji i logowania (JWT) przez endpointy Djoser.
    """

    def setUp(self):
        self.client = APIClient()

    def test_user_registration_creates_new_user(self):
        """
        Rejestracja przez POST /api/auth/users/ powinna utworzyć
        nowego użytkownika w bazie danych.
        """
        response = self.client.post('/api/auth/users/', {
            "username": "nowy_uzytkownik",
            "password": "BardzoTrudneHaslo123!",
            "email": "test@example.com",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="nowy_uzytkownik").exists())

    def test_registration_fails_with_weak_password(self):
        """
        Rejestracja z bardzo słabym, powszechnym hasłem powinna
        zostać odrzucona przez walidatory haseł Django.
        """
        response = self.client.post('/api/auth/users/', {
            "username": "slabe_haslo_user",
            "password": "12345678",
            "email": "slabe@example.com",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_valid_credentials_returns_tokens(self):
        """
        Logowanie przez POST /api/auth/jwt/create/ z poprawnymi danymi
        powinno zwrócić parę tokenów: access i refresh.
        """
        User.objects.create_user(username="testowy_user", password="BardzoTrudneHaslo123!")

        response = self.client.post('/api/auth/jwt/create/', {
            "username": "testowy_user",
            "password": "BardzoTrudneHaslo123!",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_password_returns_401(self):
        """
        Logowanie z błędnym hasłem powinno zostać odrzucone.
        """
        User.objects.create_user(username="testowy_user2", password="PoprawneHaslo123!")

        response = self.client.post('/api/auth/jwt/create/', {
            "username": "testowy_user2",
            "password": "zle_haslo",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_returns_new_access_token(self):
        """
        Wysłanie poprawnego refresh tokenu na /api/auth/jwt/refresh/
        powinno zwrócić nowy, świeży access token.
        """
        User.objects.create_user(username="refresh_user", password="BardzoTrudneHaslo123!")

        login_response = self.client.post('/api/auth/jwt/create/', {
            "username": "refresh_user",
            "password": "BardzoTrudneHaslo123!",
        })
        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post('/api/auth/jwt/refresh/', {
            "refresh": refresh_token,
        })

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data) 