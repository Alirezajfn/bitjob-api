from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_jwt_tokens_for_user(user: User) -> dict:
    """
    Returns a dictionary containing the access and refresh tokens for the given user.
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
