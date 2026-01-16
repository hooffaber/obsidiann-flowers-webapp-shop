import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProductCard } from '@/components/shop/ProductCard';
import { EmptyState } from '@/components/shop/EmptyState';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { showBackButton, hideBackButton } from '@/lib/telegram';

export default function FavoritesPage() {
  const navigate = useNavigate();
  const favorites = useFavoritesStore((state) => state.items);
  
  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md border-b border-border">
        <div className="container flex h-14 items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="font-display text-xl font-semibold">Избранное</h1>
        </div>
      </header>
      
      <main className="container py-4 pb-24">
        {favorites.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
            {favorites.map((product, index) => (
              <ProductCard 
                key={product.id} 
                product={product} 
                index={index}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Heart}
            title="Пока пусто"
            description="Добавляйте понравившиеся товары в избранное, нажимая на сердечко"
            actionLabel="Перейти в каталог"
            actionHref="/"
          />
        )}
      </main>
    </div>
  );
}
