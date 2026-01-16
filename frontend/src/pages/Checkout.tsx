import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Phone, User, MessageSquare, CreditCard, PartyPopper } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useCartStore } from '@/stores/cartStore';
import { useCreateOrder } from '@/hooks/useOrders';
import { showBackButton, hideBackButton, hapticFeedback, getTelegramUser } from '@/lib/telegram';
import { analytics } from '@/lib/analytics';
import { toast } from 'sonner';
import { z } from 'zod';
import { formatPrice } from '@/lib/utils';

const checkoutSchema = z.object({
  customer_name: z.string().min(2, 'Минимум 2 символа').max(100),
  customer_phone: z.string().regex(/^\+?[0-9\s\-\(\)]{10,}$/, 'Введите корректный номер'),
  delivery_address: z.string().min(5, 'Минимум 5 символов').max(300),
  delivery_comment: z.string().max(500).optional(),
});

type CheckoutForm = z.infer<typeof checkoutSchema>;

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, promoCode, getDiscount, getTotal, getCheckoutItems, clearCart } = useCartStore();
  const createOrder = useCreateOrder();
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);

  const [form, setForm] = useState<CheckoutForm>({
    customer_name: '',
    customer_phone: '',
    delivery_address: '',
    delivery_comment: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof CheckoutForm, string>>>({});

  useEffect(() => {
    showBackButton(() => navigate(-1));

    // Track checkout start
    analytics.trackCheckoutStart();

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

  // Redirect if cart is empty (but not during success dialog)
  useEffect(() => {
    if (!showSuccessDialog && items.length === 0) {
      navigate('/cart');
    }
  }, [items, showSuccessDialog, navigate]);

  const handleCloseSuccessDialog = () => {
    setShowSuccessDialog(false);
    clearCart();
    navigate('/');
  };

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

    try {
      const order = await createOrder.mutateAsync({
        customer_name: form.customer_name,
        customer_phone: form.customer_phone,
        delivery_address: form.delivery_address,
        delivery_comment: form.delivery_comment || undefined,
        payment_method: 'link_after_order',
        items: getCheckoutItems(),
      });

      hapticFeedback('success');
      analytics.trackOrderComplete(order.id, order.total);
      setShowSuccessDialog(true);
    } catch (error) {
      hapticFeedback('error');
      toast.error('Ошибка при оформлении заказа');
    }
  };

  return (
    <>
      {/* Success Dialog */}
      <Dialog open={showSuccessDialog} onOpenChange={(open) => !open && handleCloseSuccessDialog()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader className="text-center sm:text-center">
            <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
              <PartyPopper className="h-8 w-8 text-accent" />
            </div>
            <DialogTitle className="text-xl">Спасибо за заказ!</DialogTitle>
            <DialogDescription className="text-base pt-2">
              В ближайшее время с вами свяжется менеджер для подтверждения заказа и отправит ссылку на оплату.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-center pt-4">
            <Button onClick={handleCloseSuccessDialog} className="min-w-32">
              Отлично!
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md border-b border-border">
          <div className="container flex h-14 items-center justify-center">
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
                value={form.customer_phone}
                onChange={(e) => handleChange('customer_phone', e.target.value)}
                className={errors.customer_phone ? 'border-destructive' : ''}
              />
              {errors.customer_phone && (
                <p className="text-xs text-destructive">{errors.customer_phone}</p>
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
                value={form.delivery_address}
                onChange={(e) => handleChange('delivery_address', e.target.value)}
                className={errors.delivery_address ? 'border-destructive' : ''}
                rows={2}
              />
              {errors.delivery_address && (
                <p className="text-xs text-destructive">{errors.delivery_address}</p>
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
                value={form.delivery_comment}
                onChange={(e) => handleChange('delivery_comment', e.target.value)}
                rows={2}
              />
            </div>
          </section>

          {/* Payment Method */}
          <section className="bg-card rounded-xl p-4 shadow-card space-y-4">
            <h2 className="font-semibold text-foreground">Способ оплаты</h2>
            
            <div className="flex items-center gap-3 p-3 rounded-lg border-2 border-primary bg-primary/5">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <CreditCard className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Ссылка на оплату после заказа</p>
                <p className="text-sm text-muted-foreground">
                  Менеджер свяжется с вами в Telegram и отправит ссылку на оплату
                </p>
              </div>
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
            disabled={createOrder.isPending}
          >
            {createOrder.isPending ? 'Оформляем...' : 'Подтвердить заказ'}
          </Button>
        </div>
      </div>
      </div>
    </>
  );
}
