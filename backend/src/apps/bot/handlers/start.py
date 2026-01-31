"""
Start command handler.
"""
from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from apps.users.models import User


@sync_to_async
def _get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> User:
    """Get or create user by telegram_id and update username."""
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': f'tg_{telegram_id}',
            'telegram_username': (username or '').lower(),
            'first_name': first_name or '',
            'is_active': True,
        }
    )

    # Update username / reactivate if needed
    if not created:
        update_fields = []
        if username:
            username_lower = username.lower()
            if user.telegram_username != username_lower:
                user.telegram_username = username_lower
                update_fields.append('telegram_username')
        if not user.is_active:
            user.is_active = True
            update_fields.append('is_active')
        if update_fields:
            user.save(update_fields=update_fields)

    return user


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    tg_user = update.effective_user

    # Save/update user in database
    await _get_or_create_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
    )

    webapp_url = getattr(settings, 'TELEGRAM_MINI_APP_URL', '')

    # Build keyboard with WebApp button
    keyboard = None
    if webapp_url:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="🌸 Открыть магазин",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])

    await update.message.reply_text(
        f"Привет, {tg_user.first_name}! 👋\n\n"
        f"Добро пожаловать в бот цветочного магазина Bloom 🌸\n\n"
        f"Нажмите кнопку ниже, чтобы открыть магазин.",
        reply_markup=keyboard
    )
