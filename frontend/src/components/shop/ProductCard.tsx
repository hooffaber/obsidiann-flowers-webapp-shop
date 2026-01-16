import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Plus, Check } from 'lucide-react';
import { toast } from 'sonner';
import { Product } from '@/types/shop';
import { Button } from '@/components/ui/button';
import { useCartStore } from '@/stores/cartStore';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { hapticFeedback } from '@/lib/telegram';
import { analytics } from '@/lib/analytics';
import { cn } from '@/lib/utils';

interface ProductCardProps {
  product: Product;
  index?: number;
}

export function ProductCard({ product, index = 0 }: ProductCardProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);

  const addItem = useCartStore((state) => state.addItem);
  const { toggleFavorite, isFavorite } = useFavoritesStore();

  const isLiked = isFavorite(product.id);
  const isOutOfStock = !product.is_available;

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isOutOfStock) return;

    addItem(product);
    setAddedToCart(true);
    hapticFeedback('success');
    analytics.trackCartAdd(product.id);

    setTimeout(() => setAddedToCart(false), 1500);
  };

  const handleProductClick = () => {
    analytics.trackProductClick(product.id);
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const wasLiked = isLiked;
    toggleFavorite(product);
    hapticFeedback('light');

    if (wasLiked) {
      toast('Удалено из избранного', {
        id: 'favorite-toast',
        icon: <Heart className="h-4 w-4" />,
      });
    } else {
      toast('Добавлено в избранное', {
        id: 'favorite-toast',
        icon: <Heart className="h-4 w-4 fill-primary text-primary" />,
      });
    }
  };

  return (
    <Link
      to={`/product/${product.slug}`}
      className="group block animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
      onClick={handleProductClick}
    >
      <div className="relative h-full bg-card rounded-2xl overflow-hidden shadow-card transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 flex flex-col">
        {/* Image */}
        <div className="relative aspect-square overflow-hidden bg-muted">
          {!imageLoaded && (
            <div className="absolute inset-0 skeleton" />
          )}
          <img
            src={product.main_image || '/placeholder.jpg'}
            alt={product.title}
            loading="lazy"
            onLoad={() => setImageLoaded(true)}
            className={cn(
              "w-full h-full object-cover transition-all duration-500",
              imageLoaded ? "opacity-100 scale-100" : "opacity-0 scale-105",
              "group-hover:scale-105"
            )}
          />

          {/* Discount badge */}
          {product.has_discount && product.old_price_display && (
            <div className="absolute top-3 left-3 px-2 py-1 bg-destructive text-destructive-foreground text-xs font-medium rounded-full">
              Скидка
            </div>
          )}

          {/* Favorite Button */}
          <button
            onClick={handleToggleFavorite}
            className={cn(
              "absolute top-3 right-3 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200",
              isLiked
                ? "bg-primary text-primary-foreground"
                : "bg-background/80 backdrop-blur-sm text-foreground hover:bg-background"
            )}
          >
            <Heart className={cn("h-4 w-4", isLiked && "fill-current animate-heart")} />
          </button>

          {/* Out of Stock Overlay */}
          {isOutOfStock && (
            <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center">
              <span className="px-4 py-2 bg-muted text-muted-foreground rounded-full text-sm font-medium">
                Нет в наличии
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-3 sm:p-4 flex-1 flex flex-col">
          <h3 className="font-medium text-sm sm:text-base text-foreground line-clamp-2 mb-2 group-hover:text-primary transition-colors flex-1">
            {product.title}
          </h3>

          <div className="flex items-center justify-between gap-2 mt-auto">
            <div className="flex flex-col">
              <span className="text-sm sm:text-base font-semibold text-foreground whitespace-nowrap">
                {product.price_display}
              </span>
              {product.has_discount && product.old_price_display && (
                <span className="text-xs text-muted-foreground line-through">
                  {product.old_price_display}
                </span>
              )}
            </div>

            <Button
              size="sm"
              variant={addedToCart ? "secondary" : "default"}
              className={cn(
                "h-9 w-9 p-0 rounded-full transition-all duration-200",
                addedToCart && "bg-accent text-accent-foreground"
              )}
              onClick={handleAddToCart}
              disabled={isOutOfStock}
            >
              {addedToCart ? (
                <Check className="h-4 w-4" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </Link>
  );
}
