/**
 * React Query хуки для работы с товарами
 */
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { productsApi } from '@/lib/api';
import type { ProductsFilter, PaginatedResponse, Product } from '@/types/shop';

// Query keys
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters?: ProductsFilter) => [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (slug: string) => [...productKeys.details(), slug] as const,
  categories: ['categories'] as const,
  category: (slug: string) => [...productKeys.categories, slug] as const,
};

/**
 * Получить список категорий
 */
export function useCategories() {
  return useQuery({
    queryKey: productKeys.categories,
    queryFn: productsApi.getCategories,
    staleTime: 5 * 60 * 1000, // 5 минут
  });
}

/**
 * Получить категорию по slug
 */
export function useCategory(slug: string) {
  return useQuery({
    queryKey: productKeys.category(slug),
    queryFn: () => productsApi.getCategory(slug),
    enabled: !!slug,
  });
}

/**
 * Получить список товаров с фильтрацией
 */
export function useProducts(filters?: ProductsFilter) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productsApi.getProducts(filters),
    staleTime: 2 * 60 * 1000, // 2 минуты
  });
}

/**
 * Извлечь номер страницы из URL пагинации Django
 */
function getPageFromUrl(url: string | null): number | undefined {
  if (!url) return undefined;
  try {
    const urlObj = new URL(url);
    const page = urlObj.searchParams.get('page');
    return page ? parseInt(page, 10) : undefined;
  } catch {
    // Если URL относительный, парсим по-другому
    const match = url.match(/[?&]page=(\d+)/);
    return match ? parseInt(match[1], 10) : undefined;
  }
}

/**
 * Infinite scroll для списка товаров
 *
 * Использует useInfiniteQuery для подгрузки страниц при скролле.
 * Автоматически определяет следующую страницу из Django pagination.
 */
export function useInfiniteProducts(filters?: Omit<ProductsFilter, 'page'>) {
  return useInfiniteQuery<PaginatedResponse<Product>, Error>({
    queryKey: [...productKeys.lists(), 'infinite', filters] as const,
    queryFn: async ({ pageParam }) => {
      return productsApi.getProducts({ ...filters, page: pageParam as number });
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      // Django REST Framework возвращает URL следующей страницы или null
      return getPageFromUrl(lastPage.next);
    },
    staleTime: 2 * 60 * 1000, // 2 минуты
  });
}

/**
 * Получить товар по slug
 */
export function useProduct(slug: string) {
  return useQuery({
    queryKey: productKeys.detail(slug),
    queryFn: () => productsApi.getProduct(slug),
    enabled: !!slug,
  });
}
