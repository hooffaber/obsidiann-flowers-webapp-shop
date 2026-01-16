import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Smartphone, Check, X } from 'lucide-react';
import { Header } from '@/components/shop/Header';
import { BottomNav } from '@/components/shop/BottomNav';
import { Button } from '@/components/ui/button';
import {
  showBackButton,
  hideBackButton,
  canAddToHomeScreen,
  addToHomeScreen,
  checkHomeScreenStatus,
  hapticFeedback
} from '@/lib/telegram';
import { toast } from 'sonner';

type HomeScreenStatus = 'added' | 'missed' | 'unsupported' | 'unknown' | 'checking';

export default function SettingsPage() {
  const navigate = useNavigate();
  const [homeScreenStatus, setHomeScreenStatus] = useState<HomeScreenStatus>('checking');
  const canAdd = canAddToHomeScreen();

  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);

  useEffect(() => {
    checkHomeScreenStatus((status) => {
      setHomeScreenStatus(status);
    });
  }, []);

  const handleAddToHomeScreen = () => {
    addToHomeScreen();
    hapticFeedback('success');
    toast.success('Следуйте инструкциям на экране');

    // Проверим статус через секунду
    setTimeout(() => {
      checkHomeScreenStatus((status) => {
        setHomeScreenStatus(status);
      });
    }, 1000);
  };

  const getStatusInfo = () => {
    switch (homeScreenStatus) {
      case 'added':
        return { text: 'Уже добавлено', icon: Check, color: 'text-green-500' };
      case 'missed':
      case 'unknown':
        return { text: 'Не добавлено', icon: X, color: 'text-muted-foreground' };
      case 'unsupported':
        return { text: 'Не поддерживается', icon: X, color: 'text-muted-foreground' };
      default:
        return null;
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="min-h-screen bg-background pb-24">
      <Header showSearch={false} title="Настройки" />

      <main className="container py-6">
        {/* Home Screen Section */}
        <div className="bg-card rounded-2xl shadow-card overflow-hidden">
          <div className="p-4">
            <h2 className="font-semibold text-foreground mb-4">Быстрый доступ</h2>

            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Smartphone className="h-6 w-6 text-primary" />
              </div>

              <div className="flex-1">
                <p className="font-medium text-foreground">Добавить на главный экран</p>
                <p className="text-sm text-muted-foreground">
                  Быстрый доступ к магазину одним нажатием
                </p>
                {statusInfo && (
                  <div className={`flex items-center gap-1 mt-1 text-xs ${statusInfo.color}`}>
                    <statusInfo.icon className="h-3 w-3" />
                    {statusInfo.text}
                  </div>
                )}
              </div>
            </div>

            {canAdd && homeScreenStatus !== 'added' && (
              <Button
                className="w-full mt-4"
                onClick={handleAddToHomeScreen}
              >
                Добавить
              </Button>
            )}

            {!canAdd && (
              <p className="text-sm text-muted-foreground mt-4 p-3 bg-muted rounded-lg">
                Эта функция доступна в последней версии Telegram. Обновите приложение или добавьте вручную через меню (три точки вверху).
              </p>
            )}
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
