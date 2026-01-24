"""Users views."""
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers import TelegramAuthSerializer, UserSerializer
from apps.users.services import (
    TelegramAuthError,
    InvalidInitDataError,
    HashValidationError,
    AuthDateExpiredError,
    MissingUserDataError,
    validate_init_data,
)

logger = logging.getLogger(__name__)


class MeView(APIView):
    """Текущий пользователь."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class TelegramAuthView(APIView):
    """
    Авторизация через Telegram Mini App.

    POST /api/v1/auth/telegram/

    Принимает initData из Telegram WebApp, валидирует его
    и возвращает JWT токены.

    Request body:
        {
            "init_data": "query_id=...&user=...&auth_date=...&hash=..."
        }

    Response:
        {
            "user": {...},
            "tokens": {
                "access": "...",
                "refresh": "..."
            }
        }

    Errors:
        400 - Invalid initData format or missing required fields
        401 - Hash validation failed or auth_date expired
        500 - Server configuration error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TelegramAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        init_data = serializer.validated_data['init_data']

        # Валидация initData
        try:
            validated = validate_init_data(init_data)
        except (InvalidInitDataError, MissingUserDataError) as e:
            logger.warning(f"Invalid Telegram initData: {e}")
            return Response(
                {'error': 'invalid_init_data', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (HashValidationError, AuthDateExpiredError) as e:
            logger.warning(f"Telegram auth validation failed: {e}")
            return Response(
                {'error': 'validation_failed', 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except TelegramAuthError as e:
            logger.error(f"Telegram auth error: {e}")
            return Response(
                {'error': 'auth_error', 'detail': 'Authentication failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        telegram_user = validated.user

        # Создаём или обновляем пользователя
        user, created = User.objects.update_or_create(
            telegram_id=telegram_user.id,
            defaults={
                'first_name': telegram_user.first_name,
                'last_name': telegram_user.last_name,
                'username': telegram_user.username or f'tg_{telegram_user.id}',
            },
        )

        if created:
            logger.info(f"New user registered via Telegram: {telegram_user.id}")
        else:
            logger.debug(f"User logged in via Telegram: {telegram_user.id}")

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    """
    Обновление JWT токена.

    POST /api/v1/auth/refresh/

    Request body:
        {
            "refresh": "..."
        }

    Response:
        {
            "access": "..."
        }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'refresh_required', 'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            })
        except TokenError as e:
            return Response(
                {'error': 'invalid_token', 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class AcceptTermsView(APIView):
    """
    Принятие пользовательского соглашения.

    POST /api/v1/users/accept-terms/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone

        user = request.user
        if not user.terms_accepted:
            user.terms_accepted = True
            user.terms_accepted_at = timezone.now()
            user.save(update_fields=['terms_accepted', 'terms_accepted_at'])
            logger.info(f"User {user.id} accepted terms")

        return Response({'status': 'ok'})
