"""
Start command handler.
"""
from asgiref.sync import sync_to_async
from telegram import Update
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
        }
    )

    # Update username if changed
    if not created and username:
        username_lower = username.lower()
        if user.telegram_username != username_lower:
            user.telegram_username = username_lower
            user.save(update_fields=['telegram_username'])

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

    await update.message.reply_text(
        f"Привет, {tg_user.first_name}! 👋\n\n"
        f"Добро пожаловать в бот цветочного магазина Bloom 🌸\n\n"
        f"Нажмите кнопку ниже, чтобы открыть магазин."
    )
