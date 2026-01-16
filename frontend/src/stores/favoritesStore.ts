import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Product } from '@/types/shop';

interface FavoritesState {
  items: Product[];
  
  // Actions
  addFavorite: (product: Product) => void;
  removeFavorite: (productId: string) => void;
  toggleFavorite: (product: Product) => void;
  isFavorite: (productId: string) => boolean;
  clearFavorites: () => void;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      items: [],
      
      addFavorite: (product: Product) => {
        set((state) => {
          if (state.items.find(item => item.id === product.id)) {
            return state;
          }
          return { items: [...state.items, product] };
        });
      },
      
      removeFavorite: (productId: string) => {
        set((state) => ({
          items: state.items.filter(item => item.id !== productId),
        }));
      },
      
      toggleFavorite: (product: Product) => {
        const isFav = get().isFavorite(product.id);
        if (isFav) {
          get().removeFavorite(product.id);
        } else {
          get().addFavorite(product);
        }
      },
      
      isFavorite: (productId: string) => {
        return get().items.some(item => item.id === productId);
      },
      
      clearFavorites: () => {
        set({ items: [] });
      },
    }),
    {
      name: 'flower-shop-favorites',
    }
  )
);
