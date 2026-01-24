"""
Broadcast handler for admin mass messaging.

Uses database for conversation state (webhook-compatible).
"""
import re
from asgiref.sync import sync_to_async

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from apps.bot.models import (
    Broadcast,
    BroadcastContentType,
    BotAdmin,
    ConversationState,
)
from apps.users.models import User


# Conversation states
STATE_ENTER_USERNAMES = 'broadcast_enter_usernames'
STATE_CHOOSE_TYPE = 'broadcast_choose_type'
STATE_RECEIVE_CONTENT = 'broadcast_receive_content'
STATE_CONFIRM = 'broadcast_confirm'

# Content type mapping
CONTENT_TYPE_MAP = {
    '📝 Текст': BroadcastContentType.TEXT,
    '🖼 Фото': BroadcastContentType.PHOTO,
    '🎬 Видео': BroadcastContentType.VIDEO,
    '📎 Документ': BroadcastContentType.DOCUMENT,
    '🎤 Голосовое': BroadcastContentType.VOICE,
}

CONTENT_TYPE_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['📝 Текст', '🖼 Фото'],
        ['🎬 Видео', '📎 Документ'],
        ['🎤 Голосовое'],
        ['❌ Отмена'],
    ],
    one_time_keyboard=True,
    resize_keyboard=True,
)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup(
    [['✅ Запустить', '❌ Отмена']],
    one_time_keyboard=True,
    resize_keyboard=True,
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    one_time_keyboard=True,
    resize_keyboard=True,
)


def _parse_usernames(text: str) -> list[str]:
    """Parse usernames from text. Supports @user1 @user2 or @user1, @user2."""
    # Find all @username patterns
    pattern = r'@(\w+)'
    usernames = re.findall(pattern, text)
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for u in usernames:
        u_lower = u.lower()
        if u_lower not in seen:
            seen.add(u_lower)
            result.append(u_lower)
    return result


@sync_to_async
def _find_users_by_usernames(usernames: list[str]) -> tuple[list[dict], list[str]]:
    """
    Find users by their telegram usernames.
    Returns (found_users, not_found_usernames).
    """
    from django.db.models import Q

    found = []
    not_found = []

    for username in usernames:
        # Search in both telegram_username and username fields
        user = User.objects.filter(
            Q(telegram_username__iexact=username) | Q(username__iexact=username),
            telegram_id__isnull=False,
        ).first()

        if user:
            found.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.telegram_username or user.username,
            })
        else:
            not_found.append(username)

    return found, not_found


async def handle_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /broadcast command."""
    user = update.effective_user

    # Check admin
    admin = await BotAdmin.aget_and_update(
        telegram_id=user.id,
        username=user.username,
    )

    if not admin:
        await update.message.reply_text("⛔ У вас нет прав для создания рассылок.")
        return

    # Set state
    await ConversationState.aset_state(user.id, STATE_ENTER_USERNAMES, {})

    await update.message.reply_text(
        "📢 *Создание рассылки*\n\n"
        "*Шаг 1/3:* Введите @username получателей\n\n"
        "Формат: `@user1 @user2 @user3`\n"
        "или через запятую: `@user1, @user2, @user3`",
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all messages based on conversation state."""
    user = update.effective_user

    # Get current state
    state, data = await ConversationState.aget_state(user.id)

    if not state:
        return

    if state == STATE_ENTER_USERNAMES:
        await _handle_enter_usernames(update, user.id, data)

    elif state == STATE_CHOOSE_TYPE:
        await _handle_choose_type(update, user.id, data)

    elif state == STATE_RECEIVE_CONTENT:
        await _handle_receive_content(update, context, user.id, data)

    elif state == STATE_CONFIRM:
        await _handle_confirm(update, user.id, data)


async def _handle_enter_usernames(update: Update, user_id: int, data: dict) -> None:
    """Handle username input."""
    text = update.message.text

    if text == '❌ Отмена':
        await ConversationState.aclear(user_id)
        await update.message.reply_text(
            "Рассылка отменена.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    # Parse usernames
    usernames = _parse_usernames(text)

    if not usernames:
        await update.message.reply_text(
            "❌ Не найдено ни одного @username.\n\n"
            "Пожалуйста, введите username в формате:\n"
            "`@user1 @user2 @user3`",
            parse_mode='Markdown',
            reply_markup=CANCEL_KEYBOARD,
        )
        return

    # Find users in database
    found_users, not_found = await _find_users_by_usernames(usernames)

    if not found_users:
        await update.message.reply_text(
            f"❌ Ни один из указанных пользователей не найден в базе:\n"
            f"`{', '.join('@' + u for u in not_found)}`\n\n"
            "Убедитесь, что пользователи:\n"
            "• Запускали бота командой /start\n"
            "• Username указан правильно",
            parse_mode='Markdown',
            reply_markup=CANCEL_KEYBOARD,
        )
        return

    # Build response
    found_list = ', '.join(f"@{u['username']}" for u in found_users)
    response = f"✅ Найдено: {len(found_users)} чел.\n`{found_list}`"

    if not_found:
        not_found_list = ', '.join(f"@{u}" for u in not_found)
        response += f"\n\n⚠️ Не найдены:\n`{not_found_list}`"

    # Save found users to state
    data['recipients'] = found_users
    data['recipients_usernames'] = [u['username'] for u in found_users]
    await ConversationState.aset_state(user_id, STATE_CHOOSE_TYPE, data)

    await update.message.reply_text(
        f"{response}\n\n"
        f"*Шаг 2/3:* Выберите тип контента:",
        parse_mode='Markdown',
        reply_markup=CONTENT_TYPE_KEYBOARD,
    )


async def _handle_choose_type(update: Update, user_id: int, data: dict) -> None:
    """Handle content type selection."""
    text = update.message.text

    if text == '❌ Отмена':
        await ConversationState.aclear(user_id)
        await update.message.reply_text(
            "Рассылка отменена.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if text not in CONTENT_TYPE_MAP:
        await update.message.reply_text(
            "Пожалуйста, выберите тип из предложенных вариантов.",
            reply_markup=CONTENT_TYPE_KEYBOARD,
        )
        return

    content_type = CONTENT_TYPE_MAP[text]

    # Update state
    data['content_type'] = content_type
    await ConversationState.aset_state(user_id, STATE_RECEIVE_CONTENT, data)

    prompts = {
        BroadcastContentType.TEXT: "✏️ *Шаг 3/3:* Отправьте текст сообщения:",
        BroadcastContentType.PHOTO: "🖼 *Шаг 3/3:* Отправьте фото (можно с подписью):",
        BroadcastContentType.VIDEO: "🎬 *Шаг 3/3:* Отправьте видео (можно с подписью):",
        BroadcastContentType.DOCUMENT: "📎 *Шаг 3/3:* Отправьте документ (можно с подписью):",
        BroadcastContentType.VOICE: "🎤 *Шаг 3/3:* Отправьте голосовое сообщение:",
    }

    await update.message.reply_text(
        prompts[content_type],
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )


async def _handle_receive_content(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    data: dict,
) -> None:
    """Handle content reception."""
    message = update.message
    content_type = data.get('content_type')

    file_id = None
    text = None

    # Extract content based on type
    if content_type == BroadcastContentType.TEXT:
        if not message.text:
            await message.reply_text("❌ Пожалуйста, отправьте текстовое сообщение.")
            return
        text = message.text

    elif content_type == BroadcastContentType.PHOTO:
        if not message.photo:
            await message.reply_text("❌ Пожалуйста, отправьте фото.")
            return
        file_id = message.photo[-1].file_id
        text = message.caption or ''

    elif content_type == BroadcastContentType.VIDEO:
        if not message.video:
            await message.reply_text("❌ Пожалуйста, отправьте видео.")
            return
        file_id = message.video.file_id
        text = message.caption or ''

    elif content_type == BroadcastContentType.DOCUMENT:
        if not message.document:
            await message.reply_text("❌ Пожалуйста, отправьте документ.")
            return
        file_id = message.document.file_id
        text = message.caption or ''

    elif content_type == BroadcastContentType.VOICE:
        if not message.voice:
            await message.reply_text("❌ Пожалуйста, отправьте голосовое сообщение.")
            return
        file_id = message.voice.file_id

    # Update state with content
    data['text'] = text
    data['file_id'] = file_id
    await ConversationState.aset_state(user_id, STATE_CONFIRM, data)

    # Build summary
    recipients_count = len(data.get('recipients', []))
    recipients_usernames = data.get('recipients_usernames', [])
    recipients_list = ', '.join(f"@{u}" for u in recipients_usernames[:5])
    if len(recipients_usernames) > 5:
        recipients_list += f" и ещё {len(recipients_usernames) - 5}..."

    type_names = {
        BroadcastContentType.TEXT: 'Текст',
        BroadcastContentType.PHOTO: 'Фото',
        BroadcastContentType.VIDEO: 'Видео',
        BroadcastContentType.DOCUMENT: 'Документ',
        BroadcastContentType.VOICE: 'Голосовое',
    }

    # Send preview
    await message.reply_text(
        f"📋 *Сводка рассылки:*\n\n"
        f"👥 Получатели: *{recipients_count} чел.*\n"
        f"`{recipients_list}`\n\n"
        f"📎 Тип: *{type_names.get(content_type)}*\n\n"
        f"👁 *Предпросмотр:*",
        parse_mode='Markdown',
    )

    await _send_preview(message.chat_id, context, content_type, text, file_id)

    await message.reply_text(
        "\n✅ Запустить рассылку?",
        reply_markup=CONFIRM_KEYBOARD,
    )


async def _send_preview(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    content_type: str,
    text: str | None,
    file_id: str | None,
) -> None:
    """Send preview of the broadcast content."""
    bot = context.bot

    if content_type == BroadcastContentType.TEXT:
        await bot.send_message(chat_id=chat_id, text=text)

    elif content_type == BroadcastContentType.PHOTO:
        await bot.send_photo(chat_id=chat_id, photo=file_id, caption=text)

    elif content_type == BroadcastContentType.VIDEO:
        await bot.send_video(chat_id=chat_id, video=file_id, caption=text)

    elif content_type == BroadcastContentType.DOCUMENT:
        await bot.send_document(chat_id=chat_id, document=file_id, caption=text)

    elif content_type == BroadcastContentType.VOICE:
        await bot.send_voice(chat_id=chat_id, voice=file_id)


async def _handle_confirm(update: Update, user_id: int, data: dict) -> None:
    """Handle broadcast confirmation."""
    text = update.message.text

    if text == '❌ Отмена':
        await ConversationState.aclear(user_id)
        await update.message.reply_text(
            "Рассылка отменена.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if text != '✅ Запустить':
        await update.message.reply_text(
            "Пожалуйста, выберите действие:",
            reply_markup=CONFIRM_KEYBOARD,
        )
        return

    # Create broadcast record
    recipients_usernames = data.get('recipients_usernames', [])

    broadcast = await sync_to_async(Broadcast.objects.create)(
        recipients_usernames=recipients_usernames,
        content_type=data['content_type'],
        text=data.get('text') or '',
        file_id=data.get('file_id') or '',
        created_by_telegram_id=user_id,
    )

    # Launch Celery task
    from apps.bot.tasks import send_broadcast_task
    send_broadcast_task.delay(broadcast.id)

    recipients_count = len(recipients_usernames)

    # Clear state
    await ConversationState.aclear(user_id)

    await update.message.reply_text(
        f"🚀 *Рассылка #{broadcast.id} запущена!*\n\n"
        f"👥 Получателей: {recipients_count} чел.\n\n"
        f"Статус можно отслеживать в админ-панели.",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
