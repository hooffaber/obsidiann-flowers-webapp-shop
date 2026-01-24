"""
Telegram bot webhook views.
"""
import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from apps.bot.handlers.start import start_command
from apps.bot.handlers.broadcast import handle_broadcast_command, handle_message


logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Build a new application instance."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    application = (
        Application.builder()
        .token(token)
        .updater(None)
        .build()
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('broadcast', handle_broadcast_command))
    # Message handler for conversation flow (must be last)
    application.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.VOICE,
        handle_message,
    ))

    return application


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """Handle Telegram webhook updates."""

    async def post(self, request: HttpRequest) -> HttpResponse:
        """Process incoming webhook update."""
        try:
            data = json.loads(request.body)
            logger.debug(f"Received update: {data}")

            application = build_application()

            async with application:
                update = Update.de_json(data, application.bot)
                await application.process_update(update)

            return HttpResponse('ok')

        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook request")
            return HttpResponse('invalid json', status=400)

        except Exception as e:
            logger.exception(f"Error processing webhook: {e}")
            return HttpResponse('error', status=500)

    async def get(self, request: HttpRequest) -> JsonResponse:
        """Health check endpoint."""
        return JsonResponse({'status': 'ok', 'webhook': 'active'})


async def set_webhook(webhook_url: str) -> bool:
    """Set Telegram webhook URL."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    bot = Bot(token=token)

    async with bot:
        await bot.delete_webhook(drop_pending_updates=True)
        result = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=['message', 'callback_query'],
        )

        if result:
            logger.info(f"Webhook set successfully: {webhook_url}")
        else:
            logger.error(f"Failed to set webhook: {webhook_url}")

        return result


async def delete_webhook() -> bool:
    """Delete current webhook."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    bot = Bot(token=token)

    async with bot:
        result = await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted")
        return result


async def get_webhook_info() -> dict:
    """Get current webhook info."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    bot = Bot(token=token)

    async with bot:
        info = await bot.get_webhook_info()
        return {
            'url': info.url,
            'has_custom_certificate': info.has_custom_certificate,
            'pending_update_count': info.pending_update_count,
            'last_error_date': info.last_error_date,
            'last_error_message': info.last_error_message,
        }
