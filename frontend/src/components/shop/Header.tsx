import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, X, Menu, Info } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetClose,
} from '@/components/ui/sheet';

interface HeaderProps {
  onSearch?: (query: string) => void;
  showSearch?: boolean;
  title?: string;
}

export function Header({ onSearch, showSearch = true, title }: HeaderProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(inputValue);
  };

  return (
    <header className="sticky top-0 z-50 tg-header-offset bg-background/95 backdrop-blur-md">
      <div className="container flex h-14 items-center justify-center gap-4 relative">
        {/* Burger menu - left side */}
        <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-4"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-72 p-0 pt-20" hideCloseButton>
            {/* Custom header with close button */}
            <div className="flex items-center gap-3 p-4">
              <SheetClose asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <X className="h-5 w-5" />
                </Button>
              </SheetClose>
              <span className="font-display text-lg font-semibold tracking-wide">OBSIDIANN</span>
            </div>

            {/* Navigation */}
            <nav className="p-4 flex flex-col gap-2">
              <Link
                to="/about"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-muted transition-colors"
              >
                <Info className="h-5 w-5 text-muted-foreground" />
                <span>О нас</span>
              </Link>
            </nav>
          </SheetContent>
        </Sheet>

        {/* Logo - center */}
        <Link to="/" className="flex items-center">
          <span className="font-display text-xl font-semibold text-foreground tracking-wide">
            {title || 'OBSIDIANN'}
          </span>
        </Link>

        {/* Search button - right side (hide close button when search has text) */}
        {showSearch && !(searchOpen && inputValue) && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-4"
            onClick={() => setSearchOpen(!searchOpen)}
          >
            {searchOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Search className="h-5 w-5" />
            )}
          </Button>
        )}
      </div>

      {/* Mobile Search Bar */}
      {showSearch && searchOpen && (
        <div className="px-4 pb-3 animate-slide-up">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Найти цветы..."
                value={inputValue}
                onChange={(e) => {
                  setInputValue(e.target.value);
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
