"""
Telegram notification service for orders.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def format_price(kopeks: int) -> str:
    """Format price from kopeks to rubles."""
    rubles = kopeks // 100
    return f"{rubles:,}".replace(",", " ") + " ₽"


def send_order_notification(
    telegram_id: int,
    order_uid: str,
    items: list[dict],
    total: int,
    delivery_fee: int,
    delivery_address: str,
    delivery_date: str | None = None,
    delivery_time: str | None = None,
) -> bool:
    """
    Send order confirmation notification to user.

    Args:
        telegram_id: User's Telegram ID
        order_uid: Order UID (6-digit code)
        items: List of dicts with 'title', 'qty', 'line_total'
        total: Total amount in kopeks
        delivery_fee: Delivery fee in kopeks
        delivery_address: Delivery address
        delivery_date: Optional delivery date string
        delivery_time: Optional delivery time string

    Returns:
        True if sent successfully, False otherwise
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False

    # Build items list
    items_text = "\n".join(
        f"• {item['title']} x{item['qty']} — {format_price(item['line_total'])}"
        for item in items
    )

    # Build message
    lines = [
        f"🛍 Заказ #{order_uid} оформлен!",
        "",
        "📦 Состав:",
        items_text,
        "",
        f"💰 Итого: {format_price(total)}",
    ]

    if delivery_fee > 0:
        lines.append(f"🚚 Доставка: {format_price(delivery_fee)}")

    lines.append(f"📍 {delivery_address}")

    # Add delivery date/time if provided
    if delivery_date:
        date_line = f"📅 Доставка: {delivery_date}"
        if delivery_time:
            date_line += f", {delivery_time}"
        lines.append(date_line)

    message = "\n".join(lines)

    # Send via Telegram API
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": telegram_id,
                "text": message,
            },
            timeout=30,
        )

        if response.status_code == 200:
            logger.info(f"Order notification sent for order #{order_uid} to {telegram_id}")
            return True

        logger.error(
            f"Failed to send order notification: {response.status_code} - {response.text}"
        )
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send order notification: {e}")
        return False


STATUS_EMOJI = {
    'confirmed': '✅',
    'in_progress': '👨‍🍳',
    'delivering': '🚚',
    'done': '🎉',
    'cancelled': '❌',
}


def send_order_status_notification(
    telegram_id: int,
    order_uid: str,
    new_status: str,
    status_display: str,
    customer_phone: str | None = None,
    customer_username: str | None = None,
    order_date: str | None = None,
    items: list[dict] | None = None,
) -> bool:
    """
    Send order status change notification to user.

    Args:
        telegram_id: User's Telegram ID
        order_uid: Order UID (6-digit code)
        new_status: New status code (e.g. 'confirmed')
        status_display: Human-readable status (e.g. 'Подтверждён')
        customer_phone: Customer's phone number
        customer_username: Customer's Telegram username (without @)
        order_date: Order creation date (formatted)
        items: List of dicts with 'title', 'qty', 'line_total'

    Returns:
        True if sent successfully, False otherwise
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False

    emoji = STATUS_EMOJI.get(new_status, '📦')

    # Build message
    lines = [
        f"📦 Заказ #{order_uid}",
        "",
        f"Статус изменён: {status_display} {emoji}",
    ]

    # Build recipient line: phone + username if available
    if customer_phone and customer_username:
        lines.append(f"📱 Получатель: {customer_phone} (@{customer_username})")
    elif customer_phone:
        lines.append(f"📱 Получатель: {customer_phone}")
    elif customer_username:
        lines.append(f"📱 Получатель: @{customer_username}")

    if order_date:
        lines.append(f"📅 Дата заказа: {order_date}")

    if items:
        lines.append("")
        lines.append("🛒 Состав заказа:")
        for item in items:
            lines.append(f"• {item['title']} x{item['qty']} — {format_price(item['line_total'])}")

    message = "\n".join(lines)

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": telegram_id,
                "text": message,
            },
            timeout=30,
        )

        if response.status_code == 200:
            logger.info(f"Status notification sent for order #{order_uid} to {telegram_id}")
            return True

        logger.error(
            f"Failed to send status notification: {response.status_code} - {response.text}"
        )
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send status notification: {e}")
        return False


def send_admin_order_notification(
    order_uid: str,
    items: list[dict],
    total: int,
    delivery_fee: int,
    delivery_address: str,
    customer_name: str,
    customer_username: str | None = None,
    customer_phone: str | None = None,
    delivery_date: str | None = None,
    delivery_time: str | None = None,
) -> int:
    """
    Send order notification to all active admins.

    Args:
        order_uid: Order UID (6-digit code)
        items: List of dicts with 'title', 'qty', 'line_total'
        total: Total amount in kopeks
        delivery_fee: Delivery fee in kopeks
        delivery_address: Delivery address
        customer_name: Customer name
        customer_username: Customer's Telegram username (without @)
        customer_phone: Customer's phone number
        delivery_date: Optional delivery date string
        delivery_time: Optional delivery time string

    Returns:
        Number of admins notified successfully
    """
    from apps.bot.models import BotAdmin

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return 0

    # Get active admins with telegram_id
    admins = BotAdmin.objects.filter(is_active=True, telegram_id__isnull=False)
    if not admins.exists():
        logger.info("No active admins with telegram_id to notify")
        return 0

    # Build items list
    items_text = "\n".join(
        f"• {item['title']} x{item['qty']} — {format_price(item['line_total'])}"
        for item in items
    )

    # Customer contact: prefer username, fallback to phone
    if customer_username:
        contact = f"@{customer_username}"
    elif customer_phone:
        contact = customer_phone
    else:
        contact = "—"

    # Build message
    lines = [
        f"🆕 Новый заказ #{order_uid}",
        "",
        f"👤 Клиент: {customer_name}",
        f"📱 {contact}",
        "",
        "📦 Состав:",
        items_text,
        "",
        f"💰 Итого: {format_price(total)}",
    ]

    if delivery_fee > 0:
        lines.append(f"🚚 Доставка: {format_price(delivery_fee)}")

    lines.append(f"📍 {delivery_address}")

    # Add delivery date/time if provided
    if delivery_date:
        date_line = f"📅 {delivery_date}"
        if delivery_time:
            date_line += f", {delivery_time}"
        lines.append(date_line)

    message = "\n".join(lines)

    # Send to each admin
    sent_count = 0
    for admin in admins:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": admin.telegram_id,
                    "text": message,
                },
                timeout=30,
            )

            if response.status_code == 200:
                sent_count += 1
                logger.info(f"Admin notification sent for order #{order_uid} to {admin.username}")
            else:
                logger.error(
                    f"Failed to send admin notification to {admin.username}: "
                    f"{response.status_code} - {response.text}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send admin notification to {admin.username}: {e}")

    logger.info(f"Admin notifications sent for order #{order_uid}: {sent_count}/{admins.count()}")
    return sent_count
