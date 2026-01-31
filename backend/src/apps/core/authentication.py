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
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication

from apps.users.services import (
    TelegramAuthError,
    validate_init_data,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class DebugJWTAuthentication(BaseJWTAuthentication):
    """JWT Authentication with debug logging."""

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            logger.debug("[JWT] No Authorization header")
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            logger.debug("[JWT] No token in header")
            return None

        logger.info(f"[JWT] Token received: {raw_token[:20].decode()}...")

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.info(f"[JWT] Auth success: user_id={user.id}")
            return (user, validated_token)
        except Exception as e:
            logger.warning(f"[JWT] Auth failed: {e}")
            raise


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
            None if this authenticator doesn't apply (no initData header or invalid initData)

        Note:
            Invalid initData returns None instead of raising AuthenticationFailed.
            This allows AllowAny endpoints to work without authentication while
            IsAuthenticated endpoints will still return 401 via permission check.
        """
        init_data = self._get_init_data(request)
        if not init_data:
            return None

        # Validate initData
        try:
            validated = validate_init_data(init_data)
        except TelegramAuthError as e:
            logger.warning(f"Telegram auth failed: {e}")
            return None  # Не бросаем исключение, даём permission class решить

        # Get or create user (reactivate if was deactivated)
        try:
            user, created = User.objects.get_or_create(
                telegram_id=validated.user.id,
                defaults={
                    'first_name': validated.user.first_name,
                    'last_name': validated.user.last_name,
                    'username': f'tg_{validated.user.id}',
                    'telegram_username': (validated.user.username or '').lower(),
                    'is_active': True,
                },
            )
        except Exception as e:
            logger.error(f"Failed to get/create user: {e}")
            raise exceptions.AuthenticationFailed("User creation failed")

        if created:
            logger.info(f"New user created via Telegram header auth: {validated.user.id}")
        else:
            # Обновляем telegram_username и реактивируем если нужно
            update_fields = []
            tg_username = (validated.user.username or '').lower()
            if user.telegram_username != tg_username:
                user.telegram_username = tg_username
                update_fields.append('telegram_username')
            if not user.is_active:
                user.is_active = True
                update_fields.append('is_active')
            if update_fields:
                user.save(update_fields=update_fields)

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
