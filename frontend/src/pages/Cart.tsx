import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ShoppingBag, Tag, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CartItemComponent } from '@/components/shop/CartItem';
import { EmptyState } from '@/components/shop/EmptyState';
import { useCartStore } from '@/stores/cartStore';
import { showBackButton, hideBackButton, hapticFeedback } from '@/lib/telegram';
import { toast } from 'sonner';

// Mock promo codes
const promoCodes = {
  'BLOOM10': { code: 'BLOOM10', discount_percent: 10, is_active: true },
  'SALE500': { code: 'SALE500', fixed_amount: 500, is_active: true },
};

export default function CartPage() {
  const navigate = useNavigate();
  const [promoInput, setPromoInput] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  
  const { 
    items, 
    promoCode, 
    applyPromo, 
    removePromo,
    getSubtotal,
    getDiscount,
    getTotal 
  } = useCartStore();
  
  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);
  
  const handleApplyPromo = async () => {
    if (!promoInput.trim()) return;
    
    setPromoLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const promo = promoCodes[promoInput.toUpperCase() as keyof typeof promoCodes];
    
    if (promo && promo.is_active) {
      applyPromo(promo);
      setPromoInput('');
      hapticFeedback('success');
      toast.success('Промокод применён');
    } else {
      hapticFeedback('error');
      toast.error('Промокод не найден или истёк');
    }
    
    setPromoLoading(false);
  };
  
  const handleRemovePromo = () => {
    removePromo();
    hapticFeedback('light');
  };
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };
  
  const subtotal = getSubtotal();
  const discount = getDiscount();
  const total = getTotal();
  
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
          <h1 className="font-display text-xl font-semibold">Корзина</h1>
          {items.length > 0 && (
            <span className="text-sm text-muted-foreground">
              ({items.length})
            </span>
          )}
        </div>
      </header>
      
      <main className="container py-4 pb-48">
        {items.length > 0 ? (
          <>
            {/* Cart Items */}
            <div className="space-y-3 mb-6">
              {items.map((item, index) => (
                <CartItemComponent 
                  key={item.product_id} 
                  item={item} 
                  index={index}
                />
              ))}
            </div>
            
            {/* Promo Code */}
            <div className="bg-card rounded-xl p-4 shadow-card mb-6">
              <h3 className="font-medium text-foreground mb-3 flex items-center gap-2">
                <Tag className="h-4 w-4" />
                Промокод
              </h3>
              
              {promoCode ? (
                <div className="flex items-center justify-between bg-accent/10 rounded-lg px-4 py-3">
                  <div>
                    <span className="font-medium text-accent">{promoCode.code}</span>
                    <p className="text-sm text-muted-foreground">
                      Скидка: {formatPrice(discount)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleRemovePromo}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <Input
                    placeholder="Введите промокод"
                    value={promoInput}
                    onChange={(e) => setPromoInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleApplyPromo()}
                    className="bg-muted border-0"
                  />
                  <Button
                    variant="secondary"
                    onClick={handleApplyPromo}
                    disabled={promoLoading || !promoInput.trim()}
                  >
                    {promoLoading ? '...' : 'Применить'}
                  </Button>
                </div>
              )}
            </div>
          </>
        ) : (
          <EmptyState
            icon={ShoppingBag}
            title="Корзина пуста"
            description="Добавьте что-нибудь из каталога, чтобы оформить заказ"
            actionLabel="Перейти в каталог"
            actionHref="/"
          />
        )}
      </main>
      
      {/* Bottom Summary */}
      {items.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 safe-area-bottom bg-background border-t border-border">
          <div className="container py-4 space-y-3">
            {/* Summary */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Товары</span>
                <span>{formatPrice(subtotal)}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-accent">
                  <span>Скидка</span>
                  <span>-{formatPrice(discount)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-semibold pt-2 border-t border-border">
                <span>Итого</span>
                <span>{formatPrice(total)}</span>
              </div>
            </div>
            
            {/* Checkout Button */}
            <Button 
              size="lg" 
              className="w-full h-12"
              asChild
            >
              <Link to="/checkout">
                Оформить заказ
              </Link>
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
