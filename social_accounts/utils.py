from google.auth.transport import requests
from google.oauth2 import id_token
from accounts.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(
                access_token, requests.Request())

            if "accounts.google.com" in id_info['iss']:
                return id_info

        except Exception as e:
            return 'token is valid or has expired'


def login_social_user(email, password):
    user = authenticate(email=email, password=password)
    user_token = user.tokens()
    return {
        'email': user.email,
        'full_name': user.get_full_name,
        'access_token': str(user_token.get('access')),
        'refresh_token': str(user_token.get('refresh'))
    }


def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
        else:
            raise AuthenticationFailed(
                detail=f"please continue your login with {user[0].auth_provider}"
            )
    new_user = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': settings.SOCIAL_AUTH_PASSWORD
    }
    register_user = User.objects.create(**new_user)
    register_user.auth_provider = provider
    register_user.is_verified = True
    register_user.save()
    login_social_user(email=register_user.email,
                      password=settings.SOCIAL_AUTH_PASSWORD)
