"""
Telegram WebApp authentication for Django REST Framework.

Provides two authentication methods:
1. JWT Authentication (primary) - via JWTAuthentication from simplejwt
2. Direct initData Authentication (fallback) - via TelegramAuthentication

Usage in headers:
    Authorization: Bearer <jwt_token>  -- JWT auth (preferred)
    X-Telegram-Init-Data: <init_data>  -- Direct Telegram auth (fallback)
"""
import logging
from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from apps.users.services import (
    TelegramAuthError,
    validate_init_data,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class TelegramAuthentication(authentication.BaseAuthentication):
    """
    Telegram WebApp initData authentication.

    This authenticator validates initData directly from request headers.
    It's used as a fallback when JWT token is not available.

    The initData should be sent in the X-Telegram-Init-Data header:
        X-Telegram-Init-Data: query_id=...&user=...&auth_date=...&hash=...

    Note: For better security and performance, prefer JWT authentication.
    Use this only for initial auth or when JWT is not available.
    """

    HEADER_NAME = 'X-Telegram-Init-Data'

    def authenticate(self, request) -> Optional[Tuple[User, dict]]:
        """
        Authenticate the request using Telegram initData.

        Returns:
            Tuple of (user, auth_info) if authentication succeeds
            None if this authenticator doesn't apply (no initData header)

        Raises:
            AuthenticationFailed if initData is invalid
        """
        init_data = self._get_init_data(request)
        if not init_data:
            return None

        # Validate initData
        try:
            validated = validate_init_data(init_data)
        except TelegramAuthError as e:
            logger.warning(f"Telegram auth failed: {e}")
            raise exceptions.AuthenticationFailed(str(e))

        # Get or create user (reactivate if was deactivated)
        try:
            user, created = User.objects.get_or_create(
                telegram_id=validated.user.id,
                defaults={
                    'first_name': validated.user.first_name,
                    'last_name': validated.user.last_name,
                    'username': validated.user.username or f'tg_{validated.user.id}',
                    'is_active': True,
                },
            )
        except Exception as e:
            logger.error(f"Failed to get/create user: {e}")
            raise exceptions.AuthenticationFailed("User creation failed")

        if created:
            logger.info(f"New user created via Telegram header auth: {validated.user.id}")
        elif not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
            logger.info(f"Reactivated user via Telegram header auth: {validated.user.id}")

        # Return user and auth info
        return (user, {
            'telegram_user': validated.user,
            'auth_date': validated.auth_date,
            'auth_method': 'telegram_init_data',
        })

    def _get_init_data(self, request) -> Optional[str]:
        """Extract initData from request headers."""
        # Try standard header
        init_data = request.META.get(f'HTTP_{self.HEADER_NAME.upper().replace("-", "_")}')
        if init_data:
            return init_data

        # Try lowercase variant (some proxies lowercase headers)
        init_data = request.headers.get(self.HEADER_NAME)
        return init_data

    def authenticate_header(self, request) -> str:
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return 'TelegramInitData'
