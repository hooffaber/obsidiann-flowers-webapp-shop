"""
Middleware для ограничения доступа только из Telegram Mini App.

Проверяет наличие и валидность X-Telegram-Init-Data для всех запросов.
Можно включить/выключить через ENFORCE_TELEGRAM_ONLY в settings.

Исключения:
- /admin/ - Django admin панель
- /health/ - Health checks
- /api/schema/, /api/docs/, /api/redoc/ - API документация
- /static/, /media/ - Статические файлы
"""
import logging
from typing import Callable, Optional

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from apps.users.services import TelegramAuthError, validate_init_data

logger = logging.getLogger(__name__)


class TelegramOnlyMiddleware:
    """
    Middleware для проверки, что запрос идёт из Telegram Mini App.

    Проверяет криптографическую подпись initData, которую невозможно подделать
    без знания bot token. Простая проверка User-Agent легко обходится.
    """

    # Пути, которые доступны без Telegram
    EXCLUDED_PATHS = [
        '/admin/',
        '/health/',
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/static/',
        '/media/',
        '/tinymce/',
    ]

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.enabled = getattr(settings, 'ENFORCE_TELEGRAM_ONLY', False)

        if self.enabled:
            logger.info("🔒 Telegram-only mode enabled. Access from regular browsers blocked.")
        else:
            logger.info("🔓 Telegram-only mode disabled. Access from any browser allowed.")

    def __call__(self, request: HttpRequest):
        # Пропускаем если защита выключена
        if not self.enabled:
            return self.get_response(request)

        # Пропускаем исключённые пути
        if self._is_excluded_path(request.path):
            return self.get_response(request)

        # Проверяем наличие и валидность Telegram initData
        if not self._validate_telegram_request(request):
            return self._create_error_response(request)

        return self.get_response(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Проверить, является ли путь исключением."""
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)

    def _validate_telegram_request(self, request: HttpRequest) -> bool:
        """
        Проверить, что запрос идёт из Telegram Mini App.

        Проверяем:
        1. Наличие X-Telegram-Init-Data заголовка
        2. Валидность криптографической подписи
        3. Срок действия auth_date
        """
        # Извлекаем initData из заголовка
        init_data = self._get_init_data(request)
        if not init_data:
            logger.warning(f"Access denied: No Telegram initData. Path: {request.path}, IP: {self._get_client_ip(request)}")
            return False

        # Валидируем initData криптографически
        try:
            validated = validate_init_data(init_data)
            logger.debug(f"Valid Telegram request from user {validated.user.id}")
            return True
        except TelegramAuthError as e:
            logger.warning(f"Access denied: Invalid Telegram initData. Error: {e}, Path: {request.path}, IP: {self._get_client_ip(request)}")
            return False

    def _get_init_data(self, request: HttpRequest) -> Optional[str]:
        """Извлечь initData из заголовков запроса."""
        # Стандартный заголовок
        init_data = request.META.get('HTTP_X_TELEGRAM_INIT_DATA')
        if init_data:
            return init_data

        # Альтернативный вариант (через request.headers)
        init_data = request.headers.get('X-Telegram-Init-Data')
        return init_data

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Получить IP адрес клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def _create_error_response(self, request: HttpRequest) -> JsonResponse:
        """Создать ответ об ошибке доступа."""
        return JsonResponse(
            {
                'error': 'Telegram Required',
                'message': 'This application can only be accessed through Telegram Mini App',
                'details': {
                    'reason': 'Missing or invalid Telegram authentication data',
                    'how_to_access': 'Open this app from Telegram bot',
                },
            },
            status=403,
        )
