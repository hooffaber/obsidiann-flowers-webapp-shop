"""
Django management command to run the Telegram bot in polling mode.

NOTE: For production, use webhook mode instead:
    python manage.py setwebhook set --url https://your-domain/api/bot/webhook/
"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from telegram.ext import Application, CommandHandler

from apps.bot.handlers.start import start_command
from apps.bot.handlers.broadcast import get_broadcast_handler


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run the Telegram bot in polling mode (for development)."""

    help = 'Run the Telegram bot in polling mode (use webhook for production)'

    def handle(self, *args, **options):
        """Start the bot."""
        self.stdout.write(self.style.WARNING(
            'Running in POLLING mode. For production, use webhook:\n'
            '  python manage.py setwebhook set --url https://your-domain/api/bot/webhook/'
        ))
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('Starting Telegram bot...'))

        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not configured in settings')
            )
            return

        # Build application
        application = Application.builder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(get_broadcast_handler())

        self.stdout.write(self.style.SUCCESS('Bot started successfully!'))
        self.stdout.write('Press Ctrl+C to stop.')

        # Run the bot
        application.run_polling(drop_pending_updates=True)
