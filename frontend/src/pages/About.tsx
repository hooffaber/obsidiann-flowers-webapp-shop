import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Skeleton } from '@/components/ui/skeleton';
import { usePage } from '@/hooks/usePage';
import { showBackButton, hideBackButton } from '@/lib/telegram';

export default function AboutPage() {
  const navigate = useNavigate();
  const { data: page, isLoading, error } = usePage('about');

  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md pt-2">
          <div className="container flex h-14 items-center justify-center">
            <Skeleton className="h-6 w-32" />
          </div>
        </header>
        <main className="container py-6 space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </main>
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="font-display text-2xl font-semibold mb-2">Страница не найдена</h1>
          <p className="text-muted-foreground mb-4">Информация скоро появится</p>
          <Link to="/" className="text-primary hover:underline">
            Вернуться в каталог
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background safe-area-bottom">
      {/* Header */}
      <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md pt-2">
        <div className="container flex h-14 items-center justify-center">
          <h1 className="font-display text-xl font-semibold text-foreground">
            {page.title}
          </h1>
        </div>
      </header>

      {/* Content */}
      <main className="container py-6">
        <div
          className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-p:text-muted-foreground prose-a:text-primary"
          dangerouslySetInnerHTML={{ __html: page.content }}
        />
      </main>
    </div>
  );
}
