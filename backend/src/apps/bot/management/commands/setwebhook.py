"""
Django management command to set/delete Telegram webhook.
"""
import asyncio

from django.core.management.base import BaseCommand

from apps.bot.views import set_webhook, delete_webhook, get_webhook_info


class Command(BaseCommand):
    """Manage Telegram bot webhook."""

    help = 'Set, delete or show Telegram bot webhook'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['set', 'delete', 'info'],
            help='Action to perform: set, delete, or info',
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (required for "set" action)',
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'set':
            url = options.get('url')
            if not url:
                self.stdout.write(
                    self.style.ERROR('--url is required for "set" action')
                )
                self.stdout.write(
                    'Example: python manage.py setwebhook set --url https://your-domain.ngrok.io/api/bot/webhook/'
                )
                return

            self.stdout.write(f'Setting webhook to: {url}')
            result = asyncio.run(set_webhook(url))

            if result:
                self.stdout.write(self.style.SUCCESS('Webhook set successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to set webhook'))

        elif action == 'delete':
            self.stdout.write('Deleting webhook...')
            result = asyncio.run(delete_webhook())

            if result:
                self.stdout.write(self.style.SUCCESS('Webhook deleted successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to delete webhook'))

        elif action == 'info':
            self.stdout.write('Getting webhook info...')
            info = asyncio.run(get_webhook_info())

            self.stdout.write(self.style.SUCCESS('\nWebhook Info:'))
            self.stdout.write(f"  URL: {info['url'] or '(not set)'}")
            self.stdout.write(f"  Pending updates: {info['pending_update_count']}")

            if info['last_error_message']:
                self.stdout.write(
                    self.style.WARNING(f"  Last error: {info['last_error_message']}")
                )
