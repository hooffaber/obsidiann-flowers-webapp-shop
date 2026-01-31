/**
 * API клиент для Flower Shop
 *
 * Features:
 * - Automatic JWT token injection
 * - Token refresh on 401
 * - Fallback to Telegram initData auth
 * - Type-safe API methods
 */

import type {
  Category,
  CheckoutData,
  Order,
  OrderDetail,
  PaginatedResponse,
  Product,
  ProductsFilter,
} from '@/types/shop';
import { useAuthStore, initAuth } from '@/stores/authStore';
import { getTelegramInitData, isTelegramWebApp } from '@/lib/telegram';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

// ============ Token Refresh Lock ============

let refreshPromise: Promise<string | null> | null = null;
let initAuthPromise: Promise<void> | null = null;

async function refreshTokenWithLock(): Promise<string | null> {
  // If refresh is already in progress, wait for it
  if (refreshPromise) {
    console.log('[API] Waiting for existing refresh...');
    return refreshPromise;
  }

  console.log('[API] Starting token refresh...');

  // Start new refresh and return the NEW token directly
  refreshPromise = (async () => {
    const result = await useAuthStore.getState().refreshToken();
    if (result) {
      // Return the fresh token directly from store
      return useAuthStore.getState().getAccessToken();
    }
    return null;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function initAuthWithLock(): Promise<void> {
  // If init is already in progress, wait for it
  if (initAuthPromise) {
    return initAuthPromise;
  }

  // Start new init
  initAuthPromise = initAuth();

  try {
    await initAuthPromise;
  } finally {
    initAuthPromise = null;
  }
}

// ============ Error Handling ============

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

// ============ Request Helper ============

/**
 * Make a request with a specific token (used for retries after refresh)
 */
async function requestWithToken<T>(
  endpoint: string,
  options: RequestInit = {},
  token: string
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, data);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  retry = true
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
    ...options.headers,
  };

  // Add JWT token if available
  const accessToken = useAuthStore.getState().getAccessToken();
  if (accessToken) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
  }
  // Fallback: add Telegram initData for direct auth
  else if (isTelegramWebApp()) {
    const initData = getTelegramInitData();
    if (initData) {
      (headers as Record<string, string>)['X-Telegram-Init-Data'] = initData;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 - try to refresh token or re-authenticate
  if (response.status === 401 && retry) {
    console.log('[API] Got 401, attempting refresh...');

    if (accessToken) {
      // Has JWT - try to refresh it (with lock to prevent race conditions)
      const newToken = await refreshTokenWithLock();
      if (newToken) {
        console.log('[API] Refresh successful, retrying with new token');
        // Retry with the new token passed explicitly
        return requestWithToken<T>(endpoint, options, newToken);
      }
      console.log('[API] Refresh failed');
    } else if (isTelegramWebApp()) {
      // No JWT - try to re-init auth with fresh Telegram initData (with lock)
      console.log('[API] No token, trying Telegram re-auth...');
      await initAuthWithLock();
      const newToken = useAuthStore.getState().getAccessToken();
      if (newToken) {
        return requestWithToken<T>(endpoint, options, newToken);
      }
    }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, data);
  }

  // Handle empty responses
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ============ Products API ============

export const productsApi = {
  /**
   * Получить список категорий
   */
  getCategories: () =>
    request<Category[]>('/products/categories/'),

  /**
   * Получить категорию по slug
   */
  getCategory: (slug: string) =>
    request<Category>(`/products/categories/${slug}/`),

  /**
   * Получить список товаров
   */
  getProducts: (filters?: ProductsFilter) => {
    const params = new URLSearchParams();

    if (filters?.category) params.append('category', filters.category);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.min_price) params.append('min_price', String(filters.min_price));
    if (filters?.max_price) params.append('max_price', String(filters.max_price));
    if (filters?.in_stock) params.append('in_stock', 'true');
    if (filters?.ordering) params.append('ordering', filters.ordering);
    if (filters?.page) params.append('page', String(filters.page));

    const query = params.toString();
    return request<PaginatedResponse<Product>>(`/products/${query ? `?${query}` : ''}`);
  },

  /**
   * Получить товар по slug
   */
  getProduct: (slug: string) =>
    request<Product>(`/products/${slug}/`),
};

// ============ Orders API ============

export const ordersApi = {
  /**
   * Получить список заказов текущего пользователя
   */
  getOrders: () =>
    request<PaginatedResponse<Order>>('/orders/'),

  /**
   * Получить детали заказа
   */
  getOrder: (id: number) =>
    request<OrderDetail>(`/orders/${id}/`),

  /**
   * Создать заказ
   */
  createOrder: (data: CheckoutData) =>
    request<OrderDetail>('/orders/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ============ Favorites API ============

export const favoritesApi = {
  /**
   * Получить текущее избранное
   */
  getFavorites: () =>
    request<Product[]>('/products/favorites/'),

  /**
   * Добавить товар в избранное
   */
  addFavorite: (productId: number) =>
    request<{ detail: string; is_favorite: boolean }>('/products/favorites/', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId }),
    }),

  /**
   * Удалить товар из избранного
   */
  removeFavorite: (productId: number) =>
    request<{ detail: string; is_favorite: boolean }>(`/products/favorites/${productId}/`, {
      method: 'DELETE',
    }),

  /**
   * Синхронизировать избранное (для миграции из localStorage)
   */
  syncFavorites: (productIds: number[]) =>
    request<{ detail: string; added: number; removed: number }>('/products/favorites/sync/', {
      method: 'POST',
      body: JSON.stringify({ product_ids: productIds }),
    }),

  /**
   * Проверить статусы товаров
   */
  checkFavorites: (productIds: number[]) =>
    request<{ product_id: number; is_favorite: boolean }[]>('/products/favorites/check/', {
      method: 'POST',
      body: JSON.stringify({ product_ids: productIds }),
    }),

  /**
   * Получить историю действий с избранным
   */
  getHistory: () =>
    request<{
      id: number;
      product: Product;
      action: 'added' | 'removed';
      action_display: string;
      created_at: string;
    }[]>('/products/favorites/history/'),
};

// ============ Auth API ============

export const authApi = {
  /**
   * Авторизация через Telegram initData
   */
  loginWithTelegram: (initData: string) =>
    request<{
      user: { id: number; telegram_id: number; first_name: string; last_name: string; username: string };
      tokens: { access: string; refresh: string };
    }>('/auth/telegram/', {
      method: 'POST',
      body: JSON.stringify({ init_data: initData }),
    }),

  /**
   * Обновить access token
   */
  refreshToken: (refreshToken: string) =>
    request<{ access: string }>('/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    }),

  /**
   * Получить текущего пользователя
   */
  getMe: () =>
    request<{ id: number; telegram_id: number; first_name: string; last_name: string; username: string }>('/auth/me/'),
};

// ============ Pages API ============

export interface PageContent {
  slug: string;
  title: string;
  content: string;
}

export const pagesApi = {
  /**
   * Получить контент страницы по slug
   */
  getPage: (slug: string) =>
    request<PageContent>(`/pages/${slug}/`),
};

// ============ Export ============

export const api = {
  products: productsApi,
  orders: ordersApi,
  auth: authApi,
  favorites: favoritesApi,
  pages: pagesApi,
};

export default api;
