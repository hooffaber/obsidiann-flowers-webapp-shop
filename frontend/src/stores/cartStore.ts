import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CartItem, Product, PromoCode } from '@/types/shop';

interface CartState {
  items: CartItem[];
  promoCode: PromoCode | null;
  
  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
  applyPromo: (promo: PromoCode) => void;
  removePromo: () => void;
  
  // Computed
  getItemCount: () => number;
  getSubtotal: () => number;
  getDiscount: () => number;
  getTotal: () => number;
  
  // For checkout
  getCheckoutItems: () => { product_id: number; qty: number }[];
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      promoCode: null,
      
      addItem: (product: Product, quantity = 1) => {
        set((state) => {
          const existingItem = state.items.find(item => item.product_id === product.id);
          
          if (existingItem) {
            // Проверяем max quantity
            const maxQty = product.is_unlimited ? 99 : (product.qty_available ?? 99);
            const newQty = Math.min(existingItem.quantity + quantity, maxQty);
            
            return {
              items: state.items.map(item =>
                item.product_id === product.id
                  ? { ...item, quantity: newQty }
                  : item
              ),
            };
          }
          
          return {
            items: [...state.items, { product_id: product.id, product, quantity }],
          };
        });
      },
      
      removeItem: (productId: number) => {
        set((state) => ({
          items: state.items.filter(item => item.product_id !== productId),
        }));
        // Track cart remove
        import('@/lib/analytics').then(({ analytics }) => {
          analytics.trackCartRemove(productId);
        });
      },
      
      updateQuantity: (productId: number, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(productId);
          return;
        }
        
        set((state) => ({
          items: state.items.map(item => {
            if (item.product_id !== productId) return item;
            
            const maxQty = item.product.is_unlimited ? 99 : (item.product.qty_available ?? 99);
            return { ...item, quantity: Math.min(quantity, maxQty) };
          }),
        }));
      },
      
      clearCart: () => {
        set({ items: [], promoCode: null });
      },
      
      applyPromo: (promo: PromoCode) => {
        set({ promoCode: promo });
      },
      
      removePromo: () => {
        set({ promoCode: null });
      },
      
      getItemCount: () => {
        return get().items.reduce((sum, item) => sum + item.quantity, 0);
      },
      
      getSubtotal: () => {
        // Цены в копейках
        return get().items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
      },
      
      getDiscount: () => {
        const { promoCode } = get();
        const subtotal = get().getSubtotal();
        
        if (!promoCode) return 0;
        
        if (promoCode.discount_percent) {
          return Math.round(subtotal * (promoCode.discount_percent / 100));
        }
        
        if (promoCode.fixed_amount) {
          // fixed_amount тоже в копейках
          return Math.min(promoCode.fixed_amount, subtotal);
        }
        
        return 0;
      },
      
      getTotal: () => {
        return get().getSubtotal() - get().getDiscount();
      },
      
      getCheckoutItems: () => {
        return get().items.map(item => ({
          product_id: item.product_id,
          qty: item.quantity,
        }));
      },
    }),
    {
      name: 'flower-shop-cart',
    }
  )
);
