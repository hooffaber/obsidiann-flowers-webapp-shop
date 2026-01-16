/**
 * React Query хуки для работы с заказами
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ordersApi } from '@/lib/api';
import type { CheckoutData } from '@/types/shop';

// Query keys
export const orderKeys = {
  all: ['orders'] as const,
  lists: () => [...orderKeys.all, 'list'] as const,
  details: () => [...orderKeys.all, 'detail'] as const,
  detail: (id: number) => [...orderKeys.details(), id] as const,
};

/**
 * Получить список заказов
 */
export function useOrders() {
  return useQuery({
    queryKey: orderKeys.lists(),
    queryFn: ordersApi.getOrders,
  });
}

/**
 * Получить детали заказа
 */
export function useOrder(id: number) {
  return useQuery({
    queryKey: orderKeys.detail(id),
    queryFn: () => ordersApi.getOrder(id),
    enabled: !!id,
  });
}

/**
 * Создать заказ
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CheckoutData) => ordersApi.createOrder(data),
    onSuccess: () => {
      // Инвалидируем список заказов
      queryClient.invalidateQueries({ queryKey: orderKeys.lists() });
      // Корзина очищается в Checkout после показа диалога успеха
    },
  });
}
