import { useEffect, useState } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { initAuth } from '@/stores/authStore';
import { analytics } from '@/lib/analytics';
import { isTelegramWebApp } from '@/lib/telegram';
import { TermsAgreementDialog } from '@/components/TermsAgreementDialog';
import Index from "./pages/Index";
import Product from "./pages/Product";
import Favorites from "./pages/Favorites";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Orders from "./pages/Orders";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import About from "./pages/About";
import Oops from "./pages/Oops";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2, // 2 minutes
      retry: 1,
    },
  },
});

// Wrapper that checks Telegram access (controlled by VITE_ENFORCE_TELEGRAM_ONLY)
const ENFORCE_TELEGRAM_ONLY = import.meta.env.VITE_ENFORCE_TELEGRAM_ONLY === 'true';

function RequireTelegram({ children }: { children: React.ReactNode }) {
  if (ENFORCE_TELEGRAM_ONLY && !isTelegramWebApp()) {
    return <Navigate to="/oops" replace />;
  }
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public route - accessible without Telegram */}
      <Route path="/oops" element={<Oops />} />

      {/* Protected routes - require Telegram */}
      <Route path="/" element={<RequireTelegram><Index /></RequireTelegram>} />
      <Route path="/product/:id" element={<RequireTelegram><Product /></RequireTelegram>} />
      <Route path="/favorites" element={<RequireTelegram><Favorites /></RequireTelegram>} />
      <Route path="/cart" element={<RequireTelegram><Cart /></RequireTelegram>} />
      <Route path="/checkout" element={<RequireTelegram><Checkout /></RequireTelegram>} />
      <Route path="/orders" element={<RequireTelegram><Orders /></RequireTelegram>} />
      <Route path="/profile" element={<RequireTelegram><Profile /></RequireTelegram>} />
      <Route path="/settings" element={<RequireTelegram><Settings /></RequireTelegram>} />
      <Route path="/about" element={<RequireTelegram><About /></RequireTelegram>} />
      <Route path="*" element={<RequireTelegram><NotFound /></RequireTelegram>} />
    </Routes>
  );
}

function AppContent() {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Track app open
    analytics.trackAppOpen();

    // Initialize authentication on app start
    initAuth()
      .catch((error) => {
        console.error('Auth initialization failed:', error);
      })
      .finally(() => {
        setIsInitialized(true);
      });
  }, []);

  // Show loading while initializing auth
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">
          Загрузка...
        </div>
      </div>
    );
  }

  return (
    <>
      <TermsAgreementDialog />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner position="bottom-center" offset={80} />
      <AppContent />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
