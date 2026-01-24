import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/stores/authStore';
import { getTelegramWebApp } from '@/lib/telegram';

const TERMS_DONT_SHOW_KEY = 'bloom-terms-dont-show';
const TERMS_URL = '/terms'; // Update with actual terms page URL
const PRIVACY_URL = '/privacy'; // Update with actual privacy page URL

interface TermsAgreementDialogProps {
  onAccept?: () => void;
}

export function TermsAgreementDialog({ onAccept }: TermsAgreementDialogProps) {
  const [open, setOpen] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(true); // По умолчанию включено
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && user) {
      // Проверяем, не отключил ли пользователь показ
      const dontShow = localStorage.getItem(TERMS_DONT_SHOW_KEY);
      if (!dontShow) {
        // Показываем с небольшой задержкой для плавности
        const timer = setTimeout(() => setOpen(true), 500);
        return () => clearTimeout(timer);
      }
    }
  }, [isAuthenticated, user]);

  const handleAccept = async () => {
    // Если галочка стоит - сохраняем чтобы больше не показывать
    if (dontShowAgain) {
      localStorage.setItem(TERMS_DONT_SHOW_KEY, new Date().toISOString());
    }

    // Сохраняем на backend
    try {
      const token = useAuthStore.getState().getAccessToken();
      if (token) {
        await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/accept-terms/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Failed to save terms acceptance:', error);
    }

    setOpen(false);
    onAccept?.();
  };

  const handleDecline = () => {
    const tg = getTelegramWebApp();

    if (tg?.showConfirm) {
      tg.showConfirm(
        'Без принятия условий использование приложения невозможно. Закрыть приложение?',
        (confirmed) => {
          if (confirmed) {
            tg.close();
          }
        }
      );
    } else {
      if (confirm('Без принятия условий использование приложения невозможно. Закрыть приложение?')) {
        window.close();
      }
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) return;
    setOpen(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="sm:max-w-md mx-4 rounded-2xl"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        <DialogHeader className="text-center sm:text-center">
          <div className="mx-auto mb-4 text-5xl">🌸</div>
          <DialogTitle className="text-xl">Добро пожаловать в Bloom!</DialogTitle>
          <DialogDescription className="text-base pt-2">
            Для продолжения использования приложения необходимо принять условия
            пользовательского соглашения.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          <p className="text-sm text-muted-foreground text-center">
            Нажимая «Принять», вы соглашаетесь с{' '}
            <a
              href={TERMS_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-4 hover:text-primary/80"
            >
              условиями использования
            </a>{' '}
            и{' '}
            <a
              href={PRIVACY_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-4 hover:text-primary/80"
            >
              политикой конфиденциальности
            </a>
            .
          </p>

          {/* Чекбокс "Больше не показывать" */}
          <label className="flex items-center justify-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={dontShowAgain}
              onChange={(e) => setDontShowAgain(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
            />
            <span className="text-sm text-muted-foreground">
              Больше не показывать
            </span>
          </label>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-col">
          <Button
            onClick={handleAccept}
            className="w-full rounded-full"
            size="lg"
          >
            Принять
          </Button>
          <Button
            onClick={handleDecline}
            variant="ghost"
            className="w-full text-muted-foreground"
            size="sm"
          >
            Отклонить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
