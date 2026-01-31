"""Order DTOs."""
from dataclasses import dataclass, field
from datetime import date, datetime, time


@dataclass(frozen=True, slots=True)
class OrderItemDTO:
    """Позиция заказа."""
    id: int
    product_id: int | None
    product_title: str
    qty: int
    unit_price: int  # копейки
    line_total: int  # копейки
    image_url: str | None


@dataclass(frozen=True, slots=True)
class OrderListDTO:
    """Заказ для списка."""
    id: int
    uid: str
    status: str
    status_display: str
    total: int  # копейки
    items_count: int
    created_at: datetime
    customer_name: str


@dataclass(frozen=True)
class OrderDetailDTO:
    """Полная информация о заказе."""
    id: int
    uid: str
    status: str
    status_display: str

    # Суммы (копейки)
    subtotal: int
    delivery_fee: int
    discount: int
    total: int

    # Клиент
    customer_name: str
    customer_phone: str

    # Доставка
    delivery_address: str
    delivery_comment: str
    delivery_date: date | None
    delivery_time_from: time | None
    delivery_time_to: time | None

    # Позиции
    items: list[OrderItemDTO] = field(default_factory=list)

    # Мета
    created_at: datetime | None = None
    updated_at: datetime | None = None


# === Input DTOs ===

@dataclass(slots=True)
class OrderItemCreateDTO:
    """Позиция для создания заказа."""
    product_id: int
    qty: int = 1


@dataclass(slots=True)
class OrderCreateDTO:
    """Данные для оформления заказа."""
    customer_name: str
    customer_phone: str
    delivery_address: str
    items: list[OrderItemCreateDTO] = field(default_factory=list)
    delivery_comment: str = ''
    delivery_date: date | None = None
    delivery_time_from: time | None = None
    delivery_time_to: time | None = None


@dataclass(slots=True)
class OrderUpdateDTO:
    """Обновление заказа."""
    status: str | None = None
    delivery_fee: int | None = None
    discount: int | None = None
    delivery_date: date | None = None
    delivery_time_from: time | None = None
    delivery_time_to: time | None = None
