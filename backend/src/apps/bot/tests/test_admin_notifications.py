"""
Tests for admin order notifications.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings

from apps.bot.models import BotAdmin
from apps.bot.services.notifications import send_admin_order_notification, format_price
from apps.bot.tasks.notifications import send_admin_order_notification_task
from apps.users.models import User


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        telegram_id=123456789,
        telegram_username='testusername',
    )


@pytest.fixture
def user_without_username(db):
    """Create a test user without Telegram username."""
    return User.objects.create_user(
        username='testuser2',
        password='testpass123',
        telegram_id=987654321,
        telegram_username='',  # Empty username
    )


@pytest.fixture
def admin1(db):
    """Create first active admin with telegram_id."""
    return BotAdmin.objects.create(
        username='@admin1',
        telegram_id=111111111,
        first_name='Admin One',
        is_active=True,
    )


@pytest.fixture
def admin2(db):
    """Create second active admin with telegram_id."""
    return BotAdmin.objects.create(
        username='@admin2',
        telegram_id=222222222,
        first_name='Admin Two',
        is_active=True,
    )


@pytest.fixture
def inactive_admin(db):
    """Create inactive admin."""
    return BotAdmin.objects.create(
        username='@inactive',
        telegram_id=333333333,
        first_name='Inactive Admin',
        is_active=False,
    )


@pytest.fixture
def admin_without_telegram_id(db):
    """Create admin without telegram_id."""
    return BotAdmin.objects.create(
        username='@noid',
        telegram_id=None,
        first_name='No ID Admin',
        is_active=True,
    )


@pytest.fixture
def order_items():
    """Sample order items."""
    return [
        {'title': 'Букет роз', 'qty': 2, 'line_total': 500000},
        {'title': 'Открытка', 'qty': 1, 'line_total': 15000},
    ]


class TestFormatPrice:
    """Tests for format_price helper."""

    def test_format_price_simple(self):
        assert format_price(100) == '1 ₽'

    def test_format_price_thousands(self):
        assert format_price(150000) == '1 500 ₽'

    def test_format_price_zero(self):
        assert format_price(0) == '0 ₽'


class TestSendAdminOrderNotification:
    """Tests for send_admin_order_notification service."""

    @patch('apps.bot.services.notifications.requests.post')
    def test_sends_to_all_active_admins_with_telegram_id(
        self, mock_post, admin1, admin2, inactive_admin, admin_without_telegram_id, order_items
    ):
        """Should send notifications only to active admins with telegram_id."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = send_admin_order_notification(
            order_id=123,
            items=order_items,
            total=515000,
            delivery_fee=30000,
            delivery_address='ул. Пушкина, д. 10',
            customer_name='Иван Иванов',
            customer_username='ivan',
            customer_phone='+79991234567',
        )

        # Should send to 2 active admins with telegram_id
        assert result == 2
        assert mock_post.call_count == 2

        # Verify telegram_ids called
        called_chat_ids = [
            call[1]['json']['chat_id']
            for call in mock_post.call_args_list
        ]
        assert set(called_chat_ids) == {111111111, 222222222}

    @patch('apps.bot.services.notifications.requests.post')
    def test_message_contains_order_info(self, mock_post, admin1, order_items):
        """Should include order info in message."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_admin_order_notification(
            order_id=456,
            items=order_items,
            total=515000,
            delivery_fee=30000,
            delivery_address='ул. Ленина, д. 5',
            customer_name='Петр Петров',
            customer_username='petr',
            customer_phone='+79998887766',
            delivery_date='01.02.2026',
            delivery_time='10:00-14:00',
        )

        message = mock_post.call_args[1]['json']['text']

        # Check order ID
        assert '🆕 Новый заказ #456' in message

        # Check customer info
        assert '👤 Клиент: Петр Петров' in message
        assert '📱 @petr' in message

        # Check items
        assert 'Букет роз x2' in message
        assert 'Открытка x1' in message

        # Check totals
        assert '💰 Итого: 5 150 ₽' in message
        assert '🚚 Доставка: 300 ₽' in message

        # Check delivery info
        assert '📍 ул. Ленина, д. 5' in message
        assert '📅 01.02.2026, 10:00-14:00' in message

    @patch('apps.bot.services.notifications.requests.post')
    def test_shows_phone_when_no_username(self, mock_post, admin1, order_items):
        """Should show phone number when customer has no username."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_admin_order_notification(
            order_id=789,
            items=order_items,
            total=515000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
            customer_username=None,  # No username
            customer_phone='+79991112233',
        )

        message = mock_post.call_args[1]['json']['text']
        assert '📱 +79991112233' in message
        assert '@' not in message.split('📱')[1].split('\n')[0]

    @patch('apps.bot.services.notifications.requests.post')
    def test_shows_dash_when_no_contact(self, mock_post, admin1, order_items):
        """Should show dash when no username and no phone."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_admin_order_notification(
            order_id=111,
            items=order_items,
            total=515000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
            customer_username=None,
            customer_phone=None,
        )

        message = mock_post.call_args[1]['json']['text']
        assert '📱 —' in message

    @patch('apps.bot.services.notifications.requests.post')
    def test_hides_delivery_fee_when_zero(self, mock_post, admin1, order_items):
        """Should not show delivery fee line when it's zero."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_admin_order_notification(
            order_id=222,
            items=order_items,
            total=515000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
            customer_username='user',
        )

        message = mock_post.call_args[1]['json']['text']
        assert '🚚' not in message

    @patch('apps.bot.services.notifications.requests.post')
    def test_returns_zero_when_no_admins(self, mock_post, order_items):
        """Should return 0 when no active admins with telegram_id."""
        result = send_admin_order_notification(
            order_id=333,
            items=order_items,
            total=100000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
        )

        assert result == 0
        mock_post.assert_not_called()

    @patch('apps.bot.services.notifications.requests.post')
    def test_handles_partial_failures(self, mock_post, admin1, admin2, order_items):
        """Should count only successful sends."""
        success_response = MagicMock()
        success_response.status_code = 200

        fail_response = MagicMock()
        fail_response.status_code = 400
        fail_response.text = 'Bad request'

        mock_post.side_effect = [success_response, fail_response]

        result = send_admin_order_notification(
            order_id=444,
            items=order_items,
            total=100000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
        )

        assert result == 1

    @patch('apps.bot.services.notifications.requests.post')
    def test_handles_request_exception(self, mock_post, admin1, order_items):
        """Should handle request exceptions gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = send_admin_order_notification(
            order_id=555,
            items=order_items,
            total=100000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
        )

        assert result == 0

    @patch('apps.bot.services.notifications.settings')
    def test_returns_zero_when_no_bot_token(self, mock_settings, admin1, order_items):
        """Should return 0 when bot token is not configured."""
        mock_settings.TELEGRAM_BOT_TOKEN = None

        result = send_admin_order_notification(
            order_id=666,
            items=order_items,
            total=100000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
        )

        assert result == 0


class TestSendAdminOrderNotificationTask:
    """Tests for Celery task."""

    @patch('apps.bot.tasks.notifications.send_admin_order_notification')
    def test_task_calls_service(self, mock_service, order_items):
        """Task should call the service function with correct args."""
        mock_service.return_value = 2

        result = send_admin_order_notification_task(
            order_id=123,
            items=order_items,
            total=515000,
            delivery_fee=30000,
            delivery_address='Адрес доставки',
            customer_name='Имя Клиента',
            customer_username='username',
            customer_phone='+79991234567',
            delivery_date='01.02.2026',
            delivery_time='10:00-14:00',
        )

        assert result == 2
        mock_service.assert_called_once_with(
            order_id=123,
            items=order_items,
            total=515000,
            delivery_fee=30000,
            delivery_address='Адрес доставки',
            customer_name='Имя Клиента',
            customer_username='username',
            customer_phone='+79991234567',
            delivery_date='01.02.2026',
            delivery_time='10:00-14:00',
        )

    @patch('apps.bot.tasks.notifications.send_admin_order_notification')
    def test_task_handles_none_values(self, mock_service, order_items):
        """Task should handle None optional values."""
        mock_service.return_value = 1

        result = send_admin_order_notification_task(
            order_id=456,
            items=order_items,
            total=100000,
            delivery_fee=0,
            delivery_address='Адрес',
            customer_name='Клиент',
            customer_username=None,
            customer_phone=None,
            delivery_date=None,
            delivery_time=None,
        )

        assert result == 1


@pytest.mark.django_db
class TestOrderSerializerIntegration:
    """Integration tests for order creation with admin notifications."""

    @patch('apps.bot.tasks.notifications.send_admin_order_notification_task.delay')
    @patch('apps.bot.tasks.notifications.send_order_notification_task.delay')
    def test_order_creation_triggers_admin_notification(
        self, mock_client_task, mock_admin_task, user
    ):
        """Creating an order should trigger admin notification task."""
        from apps.orders.serializers.order import OrderCreateSerializer
        from apps.products.models import Product, Category

        # Create test product
        category = Category.objects.create(title='Test Category', slug='test')
        product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            category=category,
            price=100000,
            is_active=True,
            is_unlimited=True,
        )

        # Create order
        serializer = OrderCreateSerializer(
            data={
                'customer_name': 'Test Customer',
                'customer_phone': '+79991234567',
                'delivery_address': 'Test Address',
                'items': [{'product_id': product.id, 'qty': 1}],
            },
            context={'request': MagicMock(user=user)},
        )
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()

        # Verify admin notification was triggered
        mock_admin_task.assert_called_once()
        call_kwargs = mock_admin_task.call_args[1]

        assert call_kwargs['order_id'] == order.id
        assert call_kwargs['customer_name'] == 'Test Customer'
        assert call_kwargs['customer_username'] == 'testusername'
        assert call_kwargs['customer_phone'] == '+79991234567'
        assert call_kwargs['delivery_address'] == 'Test Address'
        assert len(call_kwargs['items']) == 1
        assert call_kwargs['items'][0]['title'] == 'Test Product'

    @patch('apps.bot.tasks.notifications.send_admin_order_notification_task.delay')
    @patch('apps.bot.tasks.notifications.send_order_notification_task.delay')
    def test_order_creation_sends_empty_username_as_none(
        self, mock_client_task, mock_admin_task, user_without_username
    ):
        """Should pass None for username when user has empty username."""
        from apps.orders.serializers.order import OrderCreateSerializer
        from apps.products.models import Product, Category

        category = Category.objects.create(title='Test Category 2', slug='test2')
        product = Product.objects.create(
            title='Test Product 2',
            slug='test-product-2',
            category=category,
            price=50000,
            is_active=True,
            is_unlimited=True,
        )

        serializer = OrderCreateSerializer(
            data={
                'customer_name': 'No Username Customer',
                'customer_phone': '+79998887766',
                'delivery_address': 'Another Address',
                'items': [{'product_id': product.id, 'qty': 2}],
            },
            context={'request': MagicMock(user=user_without_username)},
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        # Username should be None (empty string converted to None)
        call_kwargs = mock_admin_task.call_args[1]
        assert call_kwargs['customer_username'] is None

    @patch('apps.bot.tasks.notifications.send_admin_order_notification_task.delay')
    @patch('apps.bot.tasks.notifications.send_order_notification_task.delay')
    def test_order_creation_without_client_telegram_id(
        self, mock_client_task, mock_admin_task, db
    ):
        """Admin notification should work even if client has no telegram_id."""
        from apps.orders.serializers.order import OrderCreateSerializer
        from apps.products.models import Product, Category

        # User without telegram_id
        user = User.objects.create_user(
            username='notelegram',
            password='pass123',
            telegram_id=None,
            telegram_username='',
        )

        category = Category.objects.create(title='Test Category 3', slug='test3')
        product = Product.objects.create(
            title='Test Product 3',
            slug='test-product-3',
            category=category,
            price=75000,
            is_active=True,
            is_unlimited=True,
        )

        serializer = OrderCreateSerializer(
            data={
                'customer_name': 'No Telegram Customer',
                'customer_phone': '+79997776655',
                'delivery_address': 'Some Address',
                'items': [{'product_id': product.id, 'qty': 1}],
            },
            context={'request': MagicMock(user=user)},
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        # Client notification should NOT be called (no telegram_id)
        mock_client_task.assert_not_called()

        # Admin notification should still be called
        mock_admin_task.assert_called_once()
