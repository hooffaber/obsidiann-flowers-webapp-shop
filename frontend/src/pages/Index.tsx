import { useState, useRef, useEffect, useCallback } from 'react';
import { Header } from '@/components/shop/Header';
import { BottomNav } from '@/components/shop/BottomNav';
import { CategoryChips, SortOption } from '@/components/shop/CategoryChips';
import { ProductCard } from '@/components/shop/ProductCard';
import { useInfiniteProducts, useCategories } from '@/hooks/useProducts';
import { Skeleton } from '@/components/ui/skeleton';
import { Loader2 } from 'lucide-react';
import { analytics } from '@/lib/analytics';

const sortToOrdering: Record<SortOption, string | undefined> = {
  default: undefined,
  new: '-created_at',
  price_asc: 'price',
  price_desc: '-price',
};

const Index = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('default');

  // Ref для IntersectionObserver (элемент внизу списка)
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Fetch data from API
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories();
  const {
    data: productsData,
    isLoading: productsLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useInfiniteProducts({
    category: selectedCategory || undefined,
    search: searchQuery || undefined,
    ordering: sortToOrdering[sortBy],
  });

  const categories = categoriesData || [];

  // Собираем все товары из всех загруженных страниц
  const products = productsData?.pages.flatMap(page => page.results) || [];
  const totalCount = productsData?.pages[0]?.count || 0;

  // IntersectionObserver для автоматической подгрузки
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage]
  );

  useEffect(() => {
    const element = loadMoreRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(handleObserver, {
      root: null, // viewport
      rootMargin: '100px', // Начинаем загрузку за 100px до конца
      threshold: 0,
    });

    observer.observe(element);

    return () => observer.disconnect();
  }, [handleObserver]);

  // Debounce timer for search tracking
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleSearch = (query: string) => {
    setSearchQuery(query);

    // Track search with debounce
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    if (query.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        analytics.trackSearch(query);
      }, 1000);
    }
  };

  const handleCategorySelect = (slug: string | null) => {
    setSelectedCategory(slug);

    // Track category view
    if (slug) {
      const category = categories.find(c => c.slug === slug);
      if (category) {
        analytics.trackCategoryView(category.id);
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onSearch={handleSearch} />

      <main className="container py-4 pb-24">
        {/* Hero Section */}
        <section className="mb-6">
          <div className="bg-primary/10 rounded-2xl p-6 text-center">
            <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-primary mb-2">
              Цветы с доставкой
            </h1>
            <p className="text-muted-foreground text-sm sm:text-base">
              Свежие букеты для любого повода
            </p>
          </div>
        </section>

        {/* Categories & Filter */}
        <section className="mb-4">
          {categoriesLoading ? (
            <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
              <Skeleton className="h-9 w-20 rounded-full flex-shrink-0" />
              <div className="h-6 w-px bg-border flex-shrink-0" />
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-9 w-24 rounded-full flex-shrink-0" />
              ))}
            </div>
          ) : (
            <CategoryChips
              categories={categories}
              selectedSlug={selectedCategory}
              onSelect={handleCategorySelect}
              sortBy={sortBy}
              onSortChange={setSortBy}
            />
          )}
        </section>

        {/* Products Grid */}
        <section>
          {productsLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="bg-card rounded-2xl overflow-hidden shadow-card">
                  <Skeleton className="aspect-square" />
                  <div className="p-3 sm:p-4 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : products.length > 0 ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
                {products.map((product, index) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    index={index}
                  />
                ))}
              </div>

              {/* Индикатор загрузки следующей страницы */}
              {isFetchingNextPage && (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              )}

              {/* Триггер для IntersectionObserver */}
              <div ref={loadMoreRef} className="h-1" />

              {/* Показываем счётчик только когда загружены не все товары */}
              {!hasNextPage && products.length > 0 && (
                <div className="mt-6 text-center text-sm text-muted-foreground">
                  Показаны все {totalCount} товаров
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-16">
              <p className="text-muted-foreground">
                {searchQuery
                  ? 'По вашему запросу ничего не найдено'
                  : 'В этой категории пока нет товаров'}
              </p>
            </div>
          )}
        </section>
      </main>

      <BottomNav />
    </div>
  );
};

export default Index;
