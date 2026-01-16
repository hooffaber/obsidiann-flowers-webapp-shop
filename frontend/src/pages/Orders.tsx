import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Package, Clock, CheckCircle2, Truck, XCircle, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/shop/EmptyState';
import { mockOrders } from '@/data/mockData';
import { OrderStatus } from '@/types/shop';
import { showBackButton, hideBackButton } from '@/lib/telegram';
import { cn } from '@/lib/utils';

const statusConfig: Record<OrderStatus, { label: string; icon: typeof Clock; color: string }> = {
  created: { label: 'Создан', icon: Clock, color: 'text-muted-foreground' },
  confirmed: { label: 'Подтверждён', icon: CheckCircle2, color: 'text-accent' },
  delivering: { label: 'Доставляется', icon: Truck, color: 'text-primary' },
  done: { label: 'Доставлен', icon: CheckCircle2, color: 'text-accent' },
  canceled: { label: 'Отменён', icon: XCircle, color: 'text-destructive' },
};

export default function OrdersPage() {
  const navigate = useNavigate();
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null);
  
  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toggleOrder = (orderId: string) => {
    setExpandedOrder(prev => prev === orderId ? null : orderId);
  };
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md border-b border-border">
        <div className="container flex h-14 items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="font-display text-xl font-semibold">Мои заказы</h1>
        </div>
      </header>
      
      <main className="container py-4 pb-24">
        {mockOrders.length > 0 ? (
          <div className="space-y-4">
            {mockOrders.map((order, index) => {
              const status = statusConfig[order.status as OrderStatus] || statusConfig.created;
              const StatusIcon = status.icon;
              const isExpanded = expandedOrder === order.id;
              
              return (
                <div 
                  key={order.id}
                  className="bg-card rounded-xl shadow-card animate-fade-in overflow-hidden"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Clickable Header */}
                  <button
                    onClick={() => toggleOrder(order.id)}
                    className="w-full p-4 text-left"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Заказ от {formatDate(order.created_at)}
                        </p>
                        <p className="font-semibold text-lg">
                          {formatPrice(order.total_amount)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={cn("flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted text-sm", status.color)}>
                          <StatusIcon className="h-4 w-4" />
                          {status.label}
                        </div>
                        <ChevronDown className={cn(
                          "h-5 w-5 text-muted-foreground transition-transform duration-200",
                          isExpanded && "rotate-180"
                        )} />
                      </div>
                    </div>
                    
                    {/* Address */}
                    <div className="text-sm text-muted-foreground">
                      <p>{order.address}</p>
                      {order.comment && (
                        <p className="mt-1 italic">«{order.comment}»</p>
                      )}
                    </div>
                  </button>

                  {/* Expandable Items */}
                  <div className={cn(
                    "overflow-hidden transition-all duration-300",
                    isExpanded ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
                  )}>
                    <div className="px-4 pb-4 border-t border-border pt-4">
                      <h3 className="text-sm font-medium text-foreground mb-3">Состав заказа:</h3>
                      <div className="space-y-3">
                        {order.items?.map((item) => (
                          <div key={item.id} className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-lg overflow-hidden bg-muted flex-shrink-0">
                              {item.image_url && (
                                <img
                                  src={item.image_url}
                                  alt={item.title_snapshot}
                                  className="w-full h-full object-cover"
                                />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground line-clamp-1">
                                {item.title_snapshot}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {formatPrice(item.price_snapshot)} × {item.quantity} шт.
                              </p>
                            </div>
                            <div className="text-sm font-semibold text-foreground">
                              {formatPrice(item.price_snapshot * item.quantity)}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {/* Total */}
                      <div className="mt-4 pt-3 border-t border-border flex justify-between items-center">
                        <span className="font-medium text-foreground">Итого:</span>
                        <span className="text-lg font-bold text-foreground">
                          {formatPrice(order.total_amount)}
                        </span>
                      </div>
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
    </div>
  );
}
