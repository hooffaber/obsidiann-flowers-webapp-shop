import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, Clock, CheckCircle2, Truck, XCircle, ChevronDown, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Header } from '@/components/shop/Header';
import { BottomNav } from '@/components/shop/BottomNav';
import { EmptyState } from '@/components/shop/EmptyState';
import { useOrders, useOrder } from '@/hooks/useOrders';
import { OrderStatus } from '@/types/shop';
import { showBackButton, hideBackButton } from '@/lib/telegram';
import { cn } from '@/lib/utils';

const statusConfig: Record<OrderStatus, { label: string; icon: typeof Clock; bgColor: string; textColor: string }> = {
  new: { label: 'Новый', icon: Clock, bgColor: 'bg-blue-100', textColor: 'text-blue-700' },
  confirmed: { label: 'Подтверждён', icon: CheckCircle2, bgColor: 'bg-violet-100', textColor: 'text-violet-700' },
  in_progress: { label: 'Готовится', icon: Clock, bgColor: 'bg-amber-100', textColor: 'text-amber-700' },
  delivering: { label: 'Доставляется', icon: Truck, bgColor: 'bg-cyan-100', textColor: 'text-cyan-700' },
  done: { label: 'Доставлен', icon: CheckCircle2, bgColor: 'bg-green-100', textColor: 'text-green-700' },
  cancelled: { label: 'Отменён', icon: XCircle, bgColor: 'bg-red-100', textColor: 'text-red-700' },
};

function OrderItemsLoader({ orderId }: { orderId: number }) {
  const { data: orderDetail, isLoading } = useOrder(orderId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!orderDetail?.items?.length) {
    return (
      <p className="text-sm text-muted-foreground py-2">Нет информации о товарах</p>
    );
  }

  return (
    <>
      <h3 className="text-sm font-medium text-foreground mb-3">Состав заказа:</h3>
      <div className="space-y-3">
        {orderDetail.items.map((item) => (
          <div key={item.id} className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden bg-muted flex-shrink-0">
              {item.image_url && (
                <img
                  src={item.image_url}
                  alt={item.product_title}
                  className="w-full h-full object-cover"
                />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground line-clamp-1">
                {item.product_title}
              </p>
              <p className="text-xs text-muted-foreground">
                {item.unit_price_display} × {item.qty} шт.
              </p>
            </div>
            <div className="text-sm font-semibold text-foreground">
              {item.line_total_display}
            </div>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="mt-4 pt-3 border-t border-border flex justify-between items-center">
        <span className="font-medium text-foreground">Итого:</span>
        <span className="text-lg font-bold text-foreground">
          {orderDetail.total_display}
        </span>
      </div>
    </>
  );
}

export default function OrdersPage() {
  const navigate = useNavigate();
  const [expandedOrder, setExpandedOrder] = useState<number | null>(null);
  const { data: ordersData, isLoading, error } = useOrders();

  const orders = ordersData?.results || [];

  useEffect(() => {
    showBackButton(() => navigate('/profile'));
    return () => hideBackButton();
  }, [navigate]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toggleOrder = (orderId: number) => {
    setExpandedOrder(prev => prev === orderId ? null : orderId);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header showSearch={false} title="Мои заказы" />
        <main className="container py-4 pb-24">
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-card rounded-xl p-4 shadow-card space-y-3">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-6 w-24 rounded-full" />
                </div>
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-4 w-48" />
              </div>
            ))}
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Header showSearch={false} title="Мои заказы" />
        <main className="container py-4 pb-24">
          <div className="text-center py-16">
            <p className="text-muted-foreground mb-4">Не удалось загрузить заказы</p>
            <Button variant="outline" onClick={() => window.location.reload()}>
              Попробовать снова
            </Button>
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header showSearch={false} title="Мои заказы" />

      <main className="container py-4 pb-24">
        {orders.length > 0 ? (
          <div className="space-y-3">
            {orders.map((order, index) => {
              const status = statusConfig[order.status] || statusConfig.new;
              const StatusIcon = status.icon;
              const isExpanded = expandedOrder === order.id;

              return (
                <div
                  key={order.id}
                  className="bg-card rounded-2xl shadow-card animate-fade-in overflow-hidden"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Clickable Header */}
                  <button
                    onClick={() => toggleOrder(order.id)}
                    className="w-full p-4 text-left"
                  >
                    {/* Top row: Order number + Status */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-foreground">
                        Заказ #{order.id}
                      </span>
                      <div className={cn(
                        "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium",
                        status.bgColor,
                        status.textColor
                      )}>
                        <StatusIcon className="h-3.5 w-3.5" />
                        {order.status_display || status.label}
                      </div>
                    </div>

                    {/* Middle: Price + Date/Time */}
                    <div className="flex items-baseline justify-between mb-2">
                      <span className="text-xl font-bold text-foreground">
                        {order.total_display}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(order.created_at)}, {formatTime(order.created_at)}
                      </span>
                    </div>

                    {/* Bottom: Customer + Items + Chevron */}
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        <span>{order.customer_name}</span>
                        <span className="mx-1.5">•</span>
                        <span>{order.items_count} товар(ов)</span>
                      </div>
                      <ChevronDown className={cn(
                        "h-5 w-5 text-muted-foreground transition-transform duration-200",
                        isExpanded && "rotate-180"
                      )} />
                    </div>
                  </button>

                  {/* Expandable Items */}
                  <div className={cn(
                    "overflow-hidden transition-all duration-300",
                    isExpanded ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
                  )}>
                    <div className="px-4 pb-4 border-t border-border pt-4">
                      {isExpanded && <OrderItemsLoader orderId={order.id} />}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState
            icon={Package}
            title="Заказов пока нет"
            description="Оформите первый заказ, и он появится здесь"
            actionLabel="Перейти в каталог"
            actionHref="/"
          />
        )}
      </main>

      <BottomNav />
    </div>
  );
}
