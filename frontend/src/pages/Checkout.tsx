import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Phone, User, MessageSquare, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useCartStore } from '@/stores/cartStore';
import { showBackButton, hideBackButton, hapticFeedback, getTelegramUser } from '@/lib/telegram';
import { toast } from 'sonner';
import { z } from 'zod';

const checkoutSchema = z.object({
  customer_name: z.string().min(2, 'Минимум 2 символа').max(100),
  phone: z.string().regex(/^\+?[0-9\s\-\(\)]{10,}$/, 'Введите корректный номер'),
  address: z.string().min(5, 'Минимум 5 символов').max(300),
  comment: z.string().max(500).optional(),
});

type CheckoutForm = z.infer<typeof checkoutSchema>;

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, promoCode, getSubtotal, getDiscount, getTotal, clearCart } = useCartStore();
  
  const [form, setForm] = useState<CheckoutForm>({
    customer_name: '',
    phone: '',
    address: '',
    comment: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof CheckoutForm, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);
  
  useEffect(() => {
    showBackButton(() => navigate(-1));
    
    // Pre-fill from Telegram user
    const tgUser = getTelegramUser();
    if (tgUser) {
      setForm(prev => ({
        ...prev,
        customer_name: [tgUser.first_name, tgUser.last_name].filter(Boolean).join(' '),
      }));
    }
    
    return () => hideBackButton();
  }, [navigate]);
  
  // Redirect if cart is empty
  useEffect(() => {
    if (!orderPlaced && items.length === 0) {
      navigate('/cart');
    }
  }, [items, orderPlaced, navigate]);
  
  const handleChange = (field: keyof CheckoutForm, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate
    const result = checkoutSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: typeof errors = {};
      result.error.errors.forEach(err => {
        const field = err.path[0] as keyof CheckoutForm;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      hapticFeedback('error');
      return;
    }
    
    setSubmitting(true);
    
    // Simulate order creation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Success
    clearCart();
    setOrderPlaced(true);
    hapticFeedback('success');
    toast.success('Заказ оформлен!');
  };
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };
  
  if (orderPlaced) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center animate-scale-in">
          <div className="w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-6">
            <Check className="h-10 w-10 text-accent" />
          </div>
          <h1 className="font-display text-2xl font-bold text-foreground mb-2">
            Заказ оформлен!
          </h1>
          <p className="text-muted-foreground mb-6 max-w-sm">
            Мы свяжемся с вами для подтверждения доставки
          </p>
          <Button onClick={() => navigate('/')}>
            Вернуться в каталог
          </Button>
        </div>
      </div>
    );
  }
  
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
          <h1 className="font-display text-xl font-semibold">Оформление</h1>
        </div>
      </header>
      
      <main className="container py-4 pb-48">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Contact Info */}
          <section className="bg-card rounded-xl p-4 shadow-card space-y-4">
            <h2 className="font-semibold text-foreground">Контактные данные</h2>
            
            <div className="space-y-2">
              <Label htmlFor="name" className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                Имя
              </Label>
              <Input
                id="name"
                placeholder="Ваше имя"
                value={form.customer_name}
                onChange={(e) => handleChange('customer_name', e.target.value)}
                className={errors.customer_name ? 'border-destructive' : ''}
              />
              {errors.customer_name && (
                <p className="text-xs text-destructive">{errors.customer_name}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="phone" className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                Телефон
              </Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+7 (999) 123-45-67"
                value={form.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                className={errors.phone ? 'border-destructive' : ''}
              />
              {errors.phone && (
                <p className="text-xs text-destructive">{errors.phone}</p>
              )}
            </div>
          </section>
          
          {/* Delivery */}
          <section className="bg-card rounded-xl p-4 shadow-card space-y-4">
            <h2 className="font-semibold text-foreground">Доставка</h2>
            
            <div className="space-y-2">
              <Label htmlFor="address" className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                Адрес доставки
              </Label>
              <Textarea
                id="address"
                placeholder="Улица, дом, квартира"
                value={form.address}
                onChange={(e) => handleChange('address', e.target.value)}
                className={errors.address ? 'border-destructive' : ''}
                rows={2}
              />
              {errors.address && (
                <p className="text-xs text-destructive">{errors.address}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="comment" className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                Комментарий
              </Label>
              <Textarea
                id="comment"
                placeholder="Пожелания к заказу или доставке"
                value={form.comment}
                onChange={(e) => handleChange('comment', e.target.value)}
                rows={2}
              />
            </div>
          </section>
          
          {/* Order Summary */}
          <section className="bg-card rounded-xl p-4 shadow-card">
            <h2 className="font-semibold text-foreground mb-4">Ваш заказ</h2>
            
            <div className="space-y-3">
              {items.map((item) => (
                <div key={item.product_id} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    {item.product.title} × {item.quantity}
                  </span>
                  <span>{formatPrice(item.product.price * item.quantity)}</span>
                </div>
              ))}
              
              {promoCode && (
                <div className="flex justify-between text-sm text-accent">
                  <span>Промокод {promoCode.code}</span>
                  <span>-{formatPrice(getDiscount())}</span>
                </div>
              )}
            </div>
          </section>
        </form>
      </main>
      
      {/* Bottom */}
      <div className="fixed bottom-0 left-0 right-0 safe-area-bottom bg-background border-t border-border">
        <div className="container py-4 space-y-3">
          <div className="flex justify-between text-lg font-semibold">
            <span>Итого</span>
            <span>{formatPrice(getTotal())}</span>
          </div>
          
          <Button 
            size="lg" 
            className="w-full h-12"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Оформляем...' : 'Подтвердить заказ'}
          </Button>
        </div>
      </div>
    </div>
  );
}
