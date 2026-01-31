import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
        <main className="container py-6 px-4">
          <Card className="border border-border/50 shadow-sm">
            <CardContent className="p-6 space-y-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-2/3" />
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <Card className="border border-border/50 shadow-sm max-w-md w-full">
          <CardContent className="p-8 text-center">
            <h1 className="font-display text-2xl font-semibold mb-2">Страница не найдена</h1>
            <p className="text-muted-foreground mb-6">Информация скоро появится</p>
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Вернуться в каталог
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background safe-area-bottom">
      {/* Header */}
      <header className="sticky top-0 z-50 safe-area-top bg-background/95 backdrop-blur-md pt-2 border-b border-border/40">
        <div className="container flex h-14 items-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/')}
            className="mr-2"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <h1 className="font-display text-xl font-semibold text-foreground flex-1 text-center pr-10">
            {page.title}
          </h1>
        </div>
      </header>

      {/* Content */}
      <main className="container py-6 px-4">
        <Card className="border border-border/50 shadow-sm bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div
              className="prose prose-sm max-w-none text-foreground
                prose-headings:text-foreground prose-headings:font-display prose-headings:font-semibold
                prose-h2:text-lg prose-h2:mb-4 prose-h2:mt-0
                prose-p:text-muted-foreground prose-p:leading-relaxed prose-p:mb-3
                prose-a:text-primary prose-a:no-underline hover:prose-a:underline
                prose-ul:text-muted-foreground prose-li:marker:text-primary"
              dangerouslySetInnerHTML={{ __html: page.content }}
            />
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
