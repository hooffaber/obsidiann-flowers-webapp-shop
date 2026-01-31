import { Minus, Plus, Trash2 } from 'lucide-react';
import { CartItem as CartItemType } from '@/types/shop';
import { Button } from '@/components/ui/button';
import { useCartStore } from '@/stores/cartStore';
import { hapticFeedback } from '@/lib/telegram';
import { formatPrice } from '@/lib/utils';

interface CartItemProps {
  item: CartItemType;
  index?: number;
}

export function CartItemComponent({ item, index = 0 }: CartItemProps) {
  const { updateQuantity, removeItem } = useCartStore();

  const maxQuantity = item.product.is_unlimited ? 99 : (item.product.qty_available ?? 99);

  const handleIncrement = () => {
    if (item.quantity < maxQuantity) {
      updateQuantity(item.product_id, item.quantity + 1);
      hapticFeedback('light');
    }
  };

  const handleDecrement = () => {
    if (item.quantity > 1) {
      updateQuantity(item.product_id, item.quantity - 1);
      hapticFeedback('light');
    }
  };

  const handleRemove = () => {
    removeItem(item.product_id);
    hapticFeedback('medium');
  };

  return (
    <div
      className="flex gap-4 p-4 bg-card rounded-xl shadow-card animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Image */}
      <div className="w-24 h-24 flex-shrink-0 rounded-lg overflow-hidden bg-muted">
        <img
          src={item.product.main_image || '/placeholder.svg'}
          alt={item.product.title}
          className="w-full h-full object-cover"
          onError={(e) => { e.currentTarget.src = '/placeholder.svg'; }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 flex flex-col justify-between">
        <div>
          <h3 className="font-medium text-foreground line-clamp-2 text-sm">
            {item.product.title}
          </h3>
          <p className="text-sm text-muted-foreground mt-0.5">
            {item.product.price_display} × {item.quantity}
          </p>
        </div>

        <div className="flex items-center justify-between gap-4 mt-2">
          {/* Quantity Controls */}
          <div className="flex items-center gap-1 bg-muted rounded-full p-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 rounded-full"
              onClick={handleDecrement}
              disabled={item.quantity <= 1}
            >
              <Minus className="h-3.5 w-3.5" />
            </Button>
            <span className="w-8 text-center text-sm font-medium">
              {item.quantity}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 rounded-full"
              onClick={handleIncrement}
              disabled={item.quantity >= maxQuantity}
            >
              <Plus className="h-3.5 w-3.5" />
            </Button>
          </div>

          {/* Total & Remove */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-foreground truncate">
              {formatPrice(item.product.price * item.quantity)}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 flex-shrink-0 text-muted-foreground hover:text-destructive"
              onClick={handleRemove}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
