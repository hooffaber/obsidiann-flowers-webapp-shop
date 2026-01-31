import { Link } from 'react-router-dom';
import {
  User,
  Package,
  Heart,
  ChevronRight,
  LogOut,
  Settings
} from 'lucide-react';
import { Header } from '@/components/shop/Header';
import { BottomNav } from '@/components/shop/BottomNav';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useAuthStore } from '@/stores/authStore';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { useOrders } from '@/hooks/useOrders';
import { getTelegramUser } from '@/lib/telegram';

interface MenuItem {
  icon: typeof User;
  label: string;
  description?: string;
  link?: string;
  badge?: number | string;
  onClick?: () => void;
  danger?: boolean;
}

const Profile = () => {
  const { isAuthenticated, logout } = useAuthStore();
  const favoritesCount = useFavoritesStore((state) => state.items.length);
  const { data: ordersData } = useOrders();
  const telegramUser = getTelegramUser();

  const ordersCount = ordersData?.count || 0;

  const menuItems: MenuItem[] = [
    {
      icon: Package,
      label: 'Мои заказы',
      link: '/orders',
      badge: ordersCount > 0 ? ordersCount : undefined,
      description: ordersCount > 0 ? `${ordersCount} заказов` : 'Нет заказов'
    },
    {
      icon: Heart,
      label: 'Избранное',
      link: '/favorites',
      badge: favoritesCount > 0 ? favoritesCount : undefined,
      description: favoritesCount > 0 ? `${favoritesCount} товаров` : 'Нет избранных'
    },
    {
      icon: Settings,
      label: 'Настройки',
      link: '/settings',
      description: 'Быстрый доступ и другое'
    },
  ];

  const getUserInitials = () => {
    if (telegramUser?.first_name) {
      return telegramUser.first_name.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const getUserName = () => {
    if (telegramUser) {
      const parts = [telegramUser.first_name, telegramUser.last_name].filter(Boolean);
      return parts.join(' ') || telegramUser.username || 'Пользователь';
    }
    return 'Гость';
  };

  const getUserHandle = () => {
    if (telegramUser?.username) {
      return `@${telegramUser.username}`;
    }
    return null;
  };

  const renderMenuItem = (item: MenuItem, index: number) => {
    const Icon = item.icon;
    const content = (
      <div className={`
        flex items-center gap-4 p-4 rounded-xl transition-colors
        ${item.danger 
          ? 'hover:bg-destructive/10 text-destructive' 
          : 'hover:bg-muted'
        }
      `}>
        <div className={`
          w-10 h-10 rounded-full flex items-center justify-center
          ${item.danger 
            ? 'bg-destructive/10' 
            : 'bg-primary/10'
          }
        `}>
          <Icon className={`h-5 w-5 ${item.danger ? 'text-destructive' : 'text-primary'}`} />
        </div>
        <div className="flex-1">
          <div className="font-medium">{item.label}</div>
          {item.description && (
            <div className="text-sm text-muted-foreground">{item.description}</div>
          )}
        </div>
        {item.badge && (
          <div className="bg-primary text-primary-foreground text-xs font-semibold px-2.5 py-1 rounded-full">
            {item.badge}
          </div>
        )}
        {item.link && <ChevronRight className="h-5 w-5 text-muted-foreground" />}
      </div>
    );

    if (item.link) {
      return (
        <Link key={index} to={item.link}>
          {content}
        </Link>
      );
    }

    return (
      <button key={index} onClick={item.onClick} className="w-full text-left">
        {content}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      <Header showSearch={false} title="Профиль" />

      <main className="container py-6">
        {/* User Card */}
        <div className="bg-card rounded-2xl p-6 shadow-card mb-6">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            {telegramUser?.photo_url ? (
              <img 
                src={telegramUser.photo_url} 
                alt="Avatar"
                className="w-16 h-16 rounded-full object-cover"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center text-2xl font-bold text-primary-foreground">
                {getUserInitials()}
              </div>
            )}
            
            {/* Info */}
            <div className="flex-1">
              <h2 className="text-xl font-semibold">{getUserName()}</h2>
              {getUserHandle() && (
                <p className="text-muted-foreground text-sm">{getUserHandle()}</p>
              )}
              {telegramUser?.is_premium && (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-primary bg-primary/15 px-2 py-0.5 rounded-full mt-1">
                  ⭐ Premium
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Main Menu */}
        <div className="bg-card rounded-2xl shadow-card mb-6 overflow-hidden">
          {menuItems.map((item, index) => (
            <div key={index}>
              {renderMenuItem(item, index)}
              {index < menuItems.length - 1 && <Separator className="mx-4" />}
            </div>
          ))}
        </div>

        {/* Logout */}
        {isAuthenticated && (
          <Button 
            variant="ghost" 
            className="w-full text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Выйти
          </Button>
        )}

        {/* App Version */}
        <div className="text-center mt-8 text-xs text-muted-foreground">
          Obsidiann v1.0.0
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default Profile;
