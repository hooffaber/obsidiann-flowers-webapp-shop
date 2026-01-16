// Telegram WebApp integration utilities

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: TelegramUser;
    auth_date?: number;
    hash?: string;
    query_id?: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
  };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  isClosingConfirmationEnabled: boolean;
  ready: () => void;
  expand: () => void;
  close: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  MainButton: TelegramMainButton;
  BackButton: TelegramBackButton;
  HapticFeedback: TelegramHapticFeedback;
  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
  showPopup: (params: TelegramPopupParams, callback?: (buttonId: string) => void) => void;
}

export interface TelegramUser {
  id: number;
  is_bot?: boolean;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

export interface TelegramMainButton {
  text: string;
  color: string;
  textColor: string;
  isVisible: boolean;
  isActive: boolean;
  isProgressVisible: boolean;
  setText: (text: string) => void;
  onClick: (callback: () => void) => void;
  offClick: (callback: () => void) => void;
  show: () => void;
  hide: () => void;
  enable: () => void;
  disable: () => void;
  showProgress: (leaveActive?: boolean) => void;
  hideProgress: () => void;
}

export interface TelegramBackButton {
  isVisible: boolean;
  onClick: (callback: () => void) => void;
  offClick: (callback: () => void) => void;
  show: () => void;
  hide: () => void;
}

export interface TelegramHapticFeedback {
  impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
  notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
  selectionChanged: () => void;
}

export interface TelegramPopupParams {
  title?: string;
  message: string;
  buttons?: Array<{
    id?: string;
    type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
    text?: string;
  }>;
}

// Get the Telegram WebApp instance
export function getTelegramWebApp(): TelegramWebApp | null {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
}

// Check if running inside Telegram WebApp
export function isTelegramWebApp(): boolean {
  const tg = getTelegramWebApp();
  return !!tg && !!tg.initData;
}

// Get Telegram init data for API requests
export function getTelegramInitData(): string {
  const tg = getTelegramWebApp();
  return tg?.initData || '';
}

// Get current Telegram user
export function getTelegramUser(): TelegramUser | null {
  const tg = getTelegramWebApp();
  return tg?.initDataUnsafe?.user || null;
}

// Helper to compare versions
function isVersionAtLeast(current: string, required: string): boolean {
  const currentParts = current.split('.').map(Number);
  const requiredParts = required.split('.').map(Number);
  
  for (let i = 0; i < requiredParts.length; i++) {
    const curr = currentParts[i] || 0;
    const req = requiredParts[i] || 0;
    if (curr > req) return true;
    if (curr < req) return false;
  }
  return true;
}

// Initialize Telegram WebApp
export function initTelegramWebApp(): void {
  const tg = getTelegramWebApp() as any;
  if (!tg) return;

  const version = tg.version || '6.0';

  // Сообщаем что готовы
  tg.ready();

  // Разворачиваем на весь экран
  tg.expand();

  // Запрашиваем полноэкранный режим (Bot API 8.0+)
  if (isVersionAtLeast(version, '8.0') && tg.requestFullscreen) {
    try {
      tg.requestFullscreen();
    } catch (e) {
      // Ignore - not supported
    }
  }

  // Отключаем вертикальные свайпы (Bot API 7.7+)
  if (isVersionAtLeast(version, '7.7') && tg.disableVerticalSwipes) {
    try {
      tg.disableVerticalSwipes();
    } catch (e) {
      // Ignore - not supported
    }
  }

  // Устанавливаем CSS переменные для safe area (Bot API 7.0+)
  updateSafeAreaInsets(tg);

  // Слушаем изменения safe area
  if (tg.onEvent) {
    tg.onEvent('safeAreaChanged', () => updateSafeAreaInsets(tg));
    tg.onEvent('contentSafeAreaChanged', () => updateSafeAreaInsets(tg));
  }

  // Применяем тему
  if (tg.colorScheme === 'dark') {
    document.documentElement.classList.add('dark');
  }
}

// Update CSS variables for safe area insets
function updateSafeAreaInsets(tg: any): void {
  const root = document.documentElement;

  // Safe area insets (для устройств с вырезами)
  if (tg.safeAreaInset) {
    root.style.setProperty('--tg-safe-area-inset-top', `${tg.safeAreaInset.top || 0}px`);
    root.style.setProperty('--tg-safe-area-inset-bottom', `${tg.safeAreaInset.bottom || 0}px`);
    root.style.setProperty('--tg-safe-area-inset-left', `${tg.safeAreaInset.left || 0}px`);
    root.style.setProperty('--tg-safe-area-inset-right', `${tg.safeAreaInset.right || 0}px`);
  }

  // Content safe area insets (для Telegram header/footer)
  if (tg.contentSafeAreaInset) {
    root.style.setProperty('--tg-content-safe-area-inset-top', `${tg.contentSafeAreaInset.top || 0}px`);
    root.style.setProperty('--tg-content-safe-area-inset-bottom', `${tg.contentSafeAreaInset.bottom || 0}px`);
    root.style.setProperty('--tg-content-safe-area-inset-left', `${tg.contentSafeAreaInset.left || 0}px`);
    root.style.setProperty('--tg-content-safe-area-inset-right', `${tg.contentSafeAreaInset.right || 0}px`);
  }
}

// Haptic feedback helpers
export function hapticFeedback(type: 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning' | 'selection'): void {
  const tg = getTelegramWebApp();
  if (!tg?.HapticFeedback) return;
  
  switch (type) {
    case 'light':
    case 'medium':
    case 'heavy':
      tg.HapticFeedback.impactOccurred(type);
      break;
    case 'success':
    case 'error':
    case 'warning':
      tg.HapticFeedback.notificationOccurred(type);
      break;
    case 'selection':
      tg.HapticFeedback.selectionChanged();
      break;
  }
}

// Main button helpers
export function showMainButton(text: string, onClick: () => void): void {
  const tg = getTelegramWebApp();
  if (!tg?.MainButton) return;
  
  tg.MainButton.setText(text);
  tg.MainButton.onClick(onClick);
  tg.MainButton.show();
}

export function hideMainButton(): void {
  const tg = getTelegramWebApp();
  if (!tg?.MainButton) return;
  
  tg.MainButton.hide();
}

// Back button helpers
export function showBackButton(onClick: () => void): void {
  const tg = getTelegramWebApp();
  if (!tg?.BackButton) return;
  
  tg.BackButton.onClick(onClick);
  tg.BackButton.show();
}

export function hideBackButton(): void {
  const tg = getTelegramWebApp();
  if (!tg?.BackButton) return;

  tg.BackButton.hide();
}

// Add to home screen (Bot API 8.0+)
export function canAddToHomeScreen(): boolean {
  const tg = getTelegramWebApp() as any;
  return !!tg?.addToHomeScreen;
}

export function addToHomeScreen(): void {
  const tg = getTelegramWebApp() as any;
  if (tg?.addToHomeScreen) {
    tg.addToHomeScreen();
  }
}

export function checkHomeScreenStatus(callback: (status: 'added' | 'missed' | 'unsupported' | 'unknown') => void): void {
  const tg = getTelegramWebApp() as any;
  if (tg?.checkHomeScreenStatus) {
    tg.checkHomeScreenStatus(callback);
  } else {
    callback('unsupported');
  }
}
