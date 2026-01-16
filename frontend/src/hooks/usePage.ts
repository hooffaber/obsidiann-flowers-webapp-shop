/**
 * React Query хук для получения контента страниц
 */
import { useQuery } from '@tanstack/react-query';
import { pagesApi } from '@/lib/api';

export const pageKeys = {
  all: ['pages'] as const,
  page: (slug: string) => [...pageKeys.all, slug] as const,
};

/**
 * Получить контент страницы по slug
 */
export function usePage(slug: string) {
  return useQuery({
    queryKey: pageKeys.page(slug),
    queryFn: () => pagesApi.getPage(slug),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 минут
  });
}
