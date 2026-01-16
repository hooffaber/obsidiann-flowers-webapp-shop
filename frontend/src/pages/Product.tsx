import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Heart, Minus, Plus, ShoppingBag, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { products, categories } from '@/data/mockData';
import { useCartStore } from '@/stores/cartStore';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { hapticFeedback, showBackButton, hideBackButton } from '@/lib/telegram';
import { cn } from '@/lib/utils';
import { ProductImageGallery } from '@/components/shop/ProductImageGallery';

export default function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quantity, setQuantity] = useState(1);
  const [addedToCart, setAddedToCart] = useState(false);
  
  const addItem = useCartStore((state) => state.addItem);
  const { toggleFavorite, isFavorite } = useFavoritesStore();
  
  const product = products.find(p => p.id === id);
  const category = product ? categories.find(c => c.id === product.category_id) : null;
  const isLiked = product ? isFavorite(product.id) : false;
  
  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);
  
  if (!product) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="font-display text-2xl font-semibold mb-2">Товар не найден</h1>
          <Link to="/" className="text-primary hover:underline">
            Вернуться в каталог
          </Link>
        </div>
      </div>
    );
  }
  
  const handleAddToCart = () => {
    addItem(product, quantity);
    setAddedToCart(true);
    hapticFeedback('success');
    
    setTimeout(() => setAddedToCart(false), 2000);
  };
  
  const handleToggleFavorite = () => {
    toggleFavorite(product);
    hapticFeedback('light');
  };
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };
  
  const isOutOfStock = product.stock === 0;
  const maxQuantity = product.stock;
  
  // Prepare images array for gallery
  const galleryImages = product.images && product.images.length > 0 
    ? product.images 
    : [product.image_url];
  
  return (
    <div className="min-h-screen bg-background safe-area-bottom">
      {/* Header */}
      <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md border-b border-border">
        <div className="container flex h-14 items-center justify-between">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={handleToggleFavorite}
            className={cn(isLiked && "text-primary")}
          >
            <Heart className={cn("h-5 w-5", isLiked && "fill-current")} />
          </Button>
        </div>
      </header>
      
      <main className="pb-32">
        {/* Image Gallery */}
        <ProductImageGallery images={galleryImages} title={product.title} />
        
        {/* Content */}
        <div className="container py-6">
          {/* Category */}
          {category && (
            <Link 
              to={`/?category=${category.id}`}
              className="text-sm text-primary hover:underline"
            >
              {category.title}
            </Link>
          )}
          
          {/* Title */}
          <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground mt-2 mb-3">
            {product.title}
          </h1>
          
          {/* Price */}
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-2xl font-bold text-foreground">
              {formatPrice(product.price)}
            </span>
          </div>
          
          {/* Stock */}
          <div className="flex items-center gap-2 mb-6">
            <span className={cn(
              "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm",
              isOutOfStock 
                ? "bg-destructive/10 text-destructive" 
                : "bg-accent/10 text-accent"
            )}>
              <span className={cn(
                "w-2 h-2 rounded-full",
                isOutOfStock ? "bg-destructive" : "bg-accent"
              )} />
              {isOutOfStock ? 'Нет в наличии' : `В наличии: ${product.stock} шт.`}
            </span>
          </div>
          
          {/* Description */}
          <div className="mb-8">
            <h2 className="font-semibold text-foreground mb-2">Описание</h2>
            <p className="text-muted-foreground leading-relaxed">
              {product.description}
            </p>
          </div>
        </div>
      </main>
      
      {/* Bottom Actions */}
      <div className="fixed bottom-0 left-0 right-0 safe-area-bottom bg-background border-t border-border p-4">
        <div className="container flex items-center gap-4">
          {/* Quantity Selector */}
          {!isOutOfStock && (
            <div className="flex items-center gap-1 bg-muted rounded-full p-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-10 w-10 rounded-full"
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                disabled={quantity <= 1}
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="w-10 text-center font-medium">
                {quantity}
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-10 w-10 rounded-full"
                onClick={() => setQuantity(Math.min(maxQuantity, quantity + 1))}
                disabled={quantity >= maxQuantity}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          )}
          
          {/* Add to Cart Button */}
          <Button
            size="lg"
            className="flex-1 h-12 gap-2"
            onClick={handleAddToCart}
            disabled={isOutOfStock || addedToCart}
          >
            {addedToCart ? (
              <>
                <Check className="h-5 w-5" />
                Добавлено
              </>
            ) : (
              <>
                <ShoppingBag className="h-5 w-5" />
                {isOutOfStock ? 'Нет в наличии' : formatPrice(product.price * quantity)}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
