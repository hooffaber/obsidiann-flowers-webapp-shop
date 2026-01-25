"""
Django management command для управления защитой Telegram-only.

Использование:
    python manage.py telegram_protection status  # Показать текущее состояние
    python manage.py telegram_protection enable   # Включить защиту
    python manage.py telegram_protection disable  # Выключить защиту
"""
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Управление защитой доступа только из Telegram Mini App'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['status', 'enable', 'disable'],
            help='Действие: status (показать), enable (включить), disable (выключить)',
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'status':
            self.show_status()
        elif action == 'enable':
            self.enable_protection()
        elif action == 'disable':
            self.disable_protection()

    def show_status(self):
        """Показать текущее состояние защиты."""
        enabled = getattr(settings, 'ENFORCE_TELEGRAM_ONLY', False)

        if enabled:
            self.stdout.write(self.style.SUCCESS('🔒 Telegram-only защита: ВКЛЮЧЕНА'))
            self.stdout.write('   Доступ разрешён только из Telegram Mini App')
        else:
            self.stdout.write(self.style.WARNING('🔓 Telegram-only защита: ВЫКЛЮЧЕНА'))
            self.stdout.write('   Доступ разрешён из любого браузера')

        self.stdout.write('')
        self.stdout.write(f'   Источник: ENFORCE_TELEGRAM_ONLY={enabled}')
        self.stdout.write(f'   .env файл: {self._get_env_file_path()}')

    def enable_protection(self):
        """Включить защиту."""
        if self._update_env_file('ENFORCE_TELEGRAM_ONLY', 'true'):
            self.stdout.write(self.style.SUCCESS('✅ Telegram-only защита ВКЛЮЧЕНА'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  Необходимо перезапустить сервер:'))
            self.stdout.write('   docker compose restart api')
            self.stdout.write('   ИЛИ')
            self.stdout.write('   make restart')
        else:
            self.stdout.write(self.style.ERROR('❌ Не удалось обновить .env файл'))

    def disable_protection(self):
        """Выключить защиту."""
        if self._update_env_file('ENFORCE_TELEGRAM_ONLY', 'false'):
            self.stdout.write(self.style.SUCCESS('✅ Telegram-only защита ВЫКЛЮЧЕНА'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  Необходимо перезапустить сервер:'))
            self.stdout.write('   docker compose restart api')
            self.stdout.write('   ИЛИ')
            self.stdout.write('   make restart')
        else:
            self.stdout.write(self.style.ERROR('❌ Не удалось обновить .env файл'))

    def _get_env_file_path(self) -> Path:
        """Получить путь к .env файлу."""
        # backend/src -> backend/.env
        base_dir = Path(settings.BASE_DIR).parent
        return base_dir / '.env'

    def _update_env_file(self, key: str, value: str) -> bool:
        """
        Обновить значение переменной в .env файле.

        Returns:
            True если успешно, False если не удалось
        """
        env_file = self._get_env_file_path()

        if not env_file.exists():
            self.stdout.write(self.style.WARNING(f'⚠️  .env файл не найден: {env_file}'))
            self.stdout.write('   Создаю новый .env файл...')
            env_file.write_text(f'{key}={value}\n')
            return True

        # Читаем содержимое
        try:
            lines = env_file.read_text().splitlines()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка чтения .env: {e}'))
            return False

        # Обновляем или добавляем строку
        updated = False
        new_lines = []

        for line in lines:
            if line.strip().startswith(f'{key}=') or line.strip().startswith(f'# {key}='):
                new_lines.append(f'{key}={value}')
                updated = True
            else:
                new_lines.append(line)

        # Если не нашли переменную, добавляем в конец
        if not updated:
            new_lines.append(f'{key}={value}')

        # Записываем обратно
        try:
            env_file.write_text('\n'.join(new_lines) + '\n')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка записи .env: {e}'))
            return False
