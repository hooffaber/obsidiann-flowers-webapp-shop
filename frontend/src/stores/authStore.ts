import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { getTelegramInitData, isTelegramWebApp } from '@/lib/telegram';
import { initFavorites } from '@/stores/favoritesStore';

interface User {
  id: number;
  telegram_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshTokenValue: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setAuth: (user: User, tokens: { access: string; refresh: string }) => void;
  setAccessToken: (token: string) => void;
  logout: () => void;
  
  // Getters
  getAccessToken: () => string | null;
  
  // Token refresh
  refreshToken: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshTokenValue: null,
      isAuthenticated: false,
      isLoading: false,
      
      setAuth: (user, tokens) => {
        set({
          user,
          accessToken: tokens.access,
          refreshTokenValue: tokens.refresh,
          isAuthenticated: true,
        });
      },
      
      setAccessToken: (token) => {
        set({ accessToken: token });
      },
      
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshTokenValue: null,
          isAuthenticated: false,
        });
      },
      
      getAccessToken: () => get().accessToken,
      
      refreshToken: async () => {
        const refresh = get().refreshTokenValue;
        if (!refresh) return false;
        
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_URL || '/api/v1'}/auth/refresh/`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh }),
            }
          );
          
          if (!response.ok) {
            get().logout();
            return false;
          }
          
          const data = await response.json();
          set({ accessToken: data.access });
          return true;
        } catch {
          get().logout();
          return false;
        }
      },
    }),
    {
      name: 'flower-shop-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshTokenValue: state.refreshTokenValue,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

/**
 * Инициализация авторизации при запуске приложения
 */
export async function initAuth(): Promise<void> {
  // Если уже авторизован — синхронизируем избранное и выходим
  if (useAuthStore.getState().isAuthenticated) {
    await initFavorites();
    return;
  }

  // Если мы в Telegram WebApp — пытаемся авторизоваться
  if (isTelegramWebApp()) {
    const initData = getTelegramInitData();
    if (initData) {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || '/api/v1'}/auth/telegram/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ init_data: initData }),
          }
        );

        if (response.ok) {
          const data = await response.json();
          useAuthStore.getState().setAuth(data.user, data.tokens);
          // Синхронизируем избранное после успешной авторизации
          await initFavorites();
        }
      } catch (error) {
        console.error('Failed to authenticate with Telegram:', error);
      }
    }
  }
}
