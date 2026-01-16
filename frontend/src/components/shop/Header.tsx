import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Heart, ShoppingBag, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useCartStore } from '@/stores/cartStore';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onSearch?: (query: string) => void;
  showSearch?: boolean;
}

export function Header({ onSearch, showSearch = true }: HeaderProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  
  const cartItemCount = useCartStore((state) => state.getItemCount());
  const favoritesCount = useFavoritesStore((state) => state.items.length);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(searchQuery);
  };
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md border-b border-border">
      <div className="container flex h-14 items-center justify-between gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">🌸</span>
          <span className="font-display text-xl font-semibold text-foreground">
            Bloom
          </span>
        </Link>
        
        {/* Search - Desktop */}
        {showSearch && !searchOpen && (
          <form 
            onSubmit={handleSearch}
            className="hidden md:flex flex-1 max-w-md mx-4"
          >
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Найти цветы..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  onSearch?.(e.target.value);
                }}
                className="pl-10 bg-muted border-0"
              />
            </div>
          </form>
        )}
        
        {/* Actions */}
        <div className="flex items-center gap-1">
          {/* Mobile Search Toggle */}
          {showSearch && (
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setSearchOpen(!searchOpen)}
            >
              {searchOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Search className="h-5 w-5" />
              )}
            </Button>
          )}
          
          {/* Favorites */}
          <Button
            variant="ghost"
            size="icon"
            asChild
            className={cn(
              "relative",
              isActive('/favorites') && "bg-primary-soft text-primary"
            )}
          >
            <Link to="/favorites">
              <Heart className={cn("h-5 w-5", isActive('/favorites') && "fill-primary")} />
              {favoritesCount > 0 && (
                <Badge 
                  variant="default" 
                  className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
                >
                  {favoritesCount}
                </Badge>
              )}
            </Link>
          </Button>
          
          {/* Cart */}
          <Button
            variant="ghost"
            size="icon"
            asChild
            className={cn(
              "relative",
              isActive('/cart') && "bg-primary-soft text-primary"
            )}
          >
            <Link to="/cart">
              <ShoppingBag className="h-5 w-5" />
              {cartItemCount > 0 && (
                <Badge 
                  variant="default" 
                  className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
                >
                  {cartItemCount}
                </Badge>
              )}
            </Link>
          </Button>
        </div>
      </div>
      
      {/* Mobile Search Bar */}
      {showSearch && searchOpen && (
        <div className="md:hidden px-4 pb-3 animate-slide-up">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Найти цветы..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  onSearch?.(e.target.value);
                }}
                className="pl-10 bg-muted border-0"
                autoFocus
              />
            </div>
          </form>
        </div>
      )}
    </header>
  );
}
