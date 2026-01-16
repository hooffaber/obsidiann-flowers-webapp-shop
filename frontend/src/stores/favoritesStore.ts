import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Product } from '@/types/shop';
import { favoritesApi } from '@/lib/api';

interface FavoritesState {
  items: Product[];
  isLoading: boolean;
  isSynced: boolean;

  // Actions
  addFavorite: (product: Product) => void;
  removeFavorite: (productId: number) => void;
  toggleFavorite: (product: Product) => void;
  isFavorite: (productId: number) => boolean;
  clearFavorites: () => void;

  // Server sync
  syncWithServer: () => Promise<void>;
  setItems: (items: Product[]) => void;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      items: [],
      isLoading: false,
      isSynced: false,

      addFavorite: (product: Product) => {
        // Оптимистичное обновление UI
        set((state) => {
          if (state.items.find(item => item.id === product.id)) {
            return state;
          }
          return { items: [...state.items, product] };
        });

        // Отправляем на сервер если авторизован (ленивый импорт для избежания циклов)
        import('@/stores/authStore').then(({ useAuthStore }) => {
          if (useAuthStore.getState().isAuthenticated) {
            favoritesApi.addFavorite(product.id).catch((error) => {
              console.error('Failed to add favorite to server:', error);
            });
          }
        });
      },

      removeFavorite: (productId: number) => {
        // Оптимистичное обновление UI
        set((state) => ({
          items: state.items.filter(item => item.id !== productId),
        }));

        // Отправляем на сервер если авторизован (ленивый импорт для избежания циклов)
        import('@/stores/authStore').then(({ useAuthStore }) => {
          if (useAuthStore.getState().isAuthenticated) {
            favoritesApi.removeFavorite(productId).catch((error) => {
              console.error('Failed to remove favorite from server:', error);
            });
          }
        });
      },

      toggleFavorite: (product: Product) => {
        const isFav = get().isFavorite(product.id);
        if (isFav) {
          get().removeFavorite(product.id);
        } else {
          get().addFavorite(product);
        }
      },

      isFavorite: (productId: number) => {
        return get().items.some(item => item.id === productId);
      },

      clearFavorites: () => {
        set({ items: [] });
      },

      setItems: (items: Product[]) => {
        set({ items, isSynced: true });
      },

      syncWithServer: async () => {
        const { items, isSynced } = get();
        set({ isLoading: true });

        try {
          if (!isSynced && items.length > 0) {
            // Первая синхронизация - мержим локальные данные с сервером
            const productIds = items.map(item => item.id);
            await favoritesApi.syncFavorites(productIds);
          }

          // Загружаем актуальные данные с сервера
          const serverFavorites = await favoritesApi.getFavorites();
          set({ items: serverFavorites, isSynced: true, isLoading: false });
        } catch (error) {
          console.error('Failed to sync favorites with server:', error);
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'flower-shop-favorites',
      partialize: (state) => ({
        items: state.items,
        isSynced: state.isSynced,
      }),
    }
  )
);

/**
 * Инициализация избранного при запуске приложения
 * Вызывается после успешной авторизации
 */
export async function initFavorites(): Promise<void> {
  await useFavoritesStore.getState().syncWithServer();
}
