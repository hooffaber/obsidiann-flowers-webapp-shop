import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CartItem, Product, PromoCode } from '@/types/shop';

interface CartState {
  items: CartItem[];
  promoCode: PromoCode | null;
  
  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  applyPromo: (promo: PromoCode) => void;
  removePromo: () => void;
  
  // Computed
  getItemCount: () => number;
  getSubtotal: () => number;
  getDiscount: () => number;
  getTotal: () => number;
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
            return {
              items: state.items.map(item =>
                item.product_id === product.id
                  ? { ...item, quantity: Math.min(item.quantity + quantity, product.stock) }
                  : item
              ),
            };
          }
          
          return {
            items: [...state.items, { product_id: product.id, product, quantity }],
          };
        });
      },
      
      removeItem: (productId: string) => {
        set((state) => ({
          items: state.items.filter(item => item.product_id !== productId),
        }));
      },
      
      updateQuantity: (productId: string, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(productId);
          return;
        }
        
        set((state) => ({
          items: state.items.map(item =>
            item.product_id === productId
              ? { ...item, quantity: Math.min(quantity, item.product.stock) }
              : item
          ),
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
          return Math.min(promoCode.fixed_amount, subtotal);
        }
        
        return 0;
      },
      
      getTotal: () => {
        return get().getSubtotal() - get().getDiscount();
      },
    }),
    {
      name: 'flower-shop-cart',
    }
  )
);
