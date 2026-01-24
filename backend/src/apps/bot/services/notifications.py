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
    order_id: int,
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
        order_id: Order number
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
        f"🛍 Заказ #{order_id} оформлен!",
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
            logger.info(f"Order notification sent for order #{order_id} to {telegram_id}")
            return True

        logger.error(
            f"Failed to send order notification: {response.status_code} - {response.text}"
        )
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send order notification: {e}")
        return False
