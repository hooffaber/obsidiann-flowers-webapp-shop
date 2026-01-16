import { useState, useMemo, useEffect } from 'react';
import { Header } from '@/components/shop/Header';
import { CategoryChips } from '@/components/shop/CategoryChips';
import { ProductCard } from '@/components/shop/ProductCard';
import { categories, products } from '@/data/mockData';
import { initTelegramWebApp } from '@/lib/telegram';

type SortOption = 'default' | 'new' | 'price_asc' | 'price_desc';

const Index = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('default');
  
  useEffect(() => {
    initTelegramWebApp();
  }, []);
  
  const filteredProducts = useMemo(() => {
    let result = products.filter(p => p.is_active);
    
    // Filter by category
    if (selectedCategory) {
      result = result.filter(p => p.category_id === selectedCategory);
    }
    
    // Filter by search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(p => 
        p.title.toLowerCase().includes(query) ||
        p.description.toLowerCase().includes(query)
      );
    }
    
    // Sort
    switch (sortBy) {
      case 'new':
        result = [...result].sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        break;
      case 'price_asc':
        result = [...result].sort((a, b) => a.price - b.price);
        break;
      case 'price_desc':
        result = [...result].sort((a, b) => b.price - a.price);
        break;
      default:
        // Default: hits first, then new
        result = [...result].sort((a, b) => {
          if (a.is_hit && !b.is_hit) return -1;
          if (!a.is_hit && b.is_hit) return 1;
          if (a.is_new && !b.is_new) return -1;
          if (!a.is_new && b.is_new) return 1;
          return 0;
        });
    }
    
    return result;
  }, [selectedCategory, searchQuery, sortBy]);

  return (
    <div className="min-h-screen bg-background">
      <Header onSearch={setSearchQuery} />
      
      <main className="container py-4 pb-24">
        {/* Hero Section */}
        <section className="mb-6">
          <div className="gradient-hero rounded-2xl p-6 text-center">
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-2">
              Цветы с доставкой
            </h1>
            <p className="text-muted-foreground">
              Свежие букеты для любого повода
            </p>
          </div>
        </section>
        
        {/* Categories */}
        <section className="mb-6">
          <CategoryChips
            categories={categories}
            selectedId={selectedCategory}
            onSelect={setSelectedCategory}
          />
        </section>
        
        {/* Sort Options */}
        <section className="flex items-center gap-2 mb-4 overflow-x-auto pb-1 -mx-4 px-4">
          {[
            { value: 'default', label: 'По умолчанию' },
            { value: 'new', label: 'Новинки' },
            { value: 'price_asc', label: 'Дешевле' },
            { value: 'price_desc', label: 'Дороже' },
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => setSortBy(option.value as SortOption)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                sortBy === option.value
                  ? 'bg-secondary text-secondary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {option.label}
            </button>
          ))}
        </section>
        
        {/* Products Grid */}
        <section>
          {filteredProducts.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
              {filteredProducts.map((product, index) => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  index={index}
                />
              ))}
            </div>
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
    </div>
  );
};

export default Index;
