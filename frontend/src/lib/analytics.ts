/**
 * Analytics tracking service
 *
 * Отправляет события на сервер для аналитики.
 * Использует батчинг для уменьшения количества запросов.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

// Типы событий (должны совпадать с бэкендом)
export type EventType =
  | 'app_open'
  | 'product_view'
  | 'product_click'
  | 'cart_add'
  | 'cart_remove'
  | 'category_view'
  | 'search'
  | 'checkout_start'
  | 'order_complete';

interface AnalyticsEvent {
  event_type: EventType;
  product_id?: number;
  category_id?: number;
  search_query?: string;
  metadata?: Record<string, unknown>;
}

// Очередь событий для батчинга
let eventQueue: AnalyticsEvent[] = [];
let flushTimeout: ReturnType<typeof setTimeout> | null = null;

// Получаем или создаём session_id
function getSessionId(): string {
  let sessionId = sessionStorage.getItem('analytics_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem('analytics_session_id', sessionId);
  }
  return sessionId;
}

// Получаем auth headers
function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const authData = localStorage.getItem('flower-shop-auth');
  if (authData) {
    try {
      const { state } = JSON.parse(authData);
      if (state?.accessToken) {
        headers['Authorization'] = `Bearer ${state.accessToken}`;
      }
    } catch {
      // Ignore parse errors
    }
  }

  return headers;
}

// Отправка событий на сервер
async function flushEvents(): Promise<void> {
  if (eventQueue.length === 0) return;

  const events = [...eventQueue];
  eventQueue = [];

  if (flushTimeout) {
    clearTimeout(flushTimeout);
    flushTimeout = null;
  }

  try {
    const sessionId = getSessionId();

    // Добавляем session_id ко всем событиям
    const eventsWithSession = events.map(e => ({
      ...e,
      session_id: sessionId,
    }));

    await fetch(`${API_BASE}/analytics/track/batch/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ events: eventsWithSession }),
    });
  } catch (error) {
    // Не блокируем UI при ошибках аналитики
    console.warn('Failed to send analytics:', error);
  }
}

// Немедленная отправка одного события (без батчинга)
async function sendEventImmediately(event: AnalyticsEvent): Promise<void> {
  try {
    const sessionId = getSessionId();

    await fetch(`${API_BASE}/analytics/track/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        ...event,
        session_id: sessionId,
      }),
    });
  } catch (error) {
    console.warn('Failed to send analytics:', error);
  }
}

// Добавить событие в очередь
function queueEvent(event: AnalyticsEvent, immediate = false): void {
  // Для важных событий отправляем сразу
  if (immediate) {
    sendEventImmediately(event);
    return;
  }

  eventQueue.push(event);

  // Debounce - отправляем через 500ms после последнего события (было 2000)
  if (flushTimeout) {
    clearTimeout(flushTimeout);
  }
  flushTimeout = setTimeout(flushEvents, 500);

  // Принудительная отправка если накопилось много событий
  if (eventQueue.length >= 5) {
    if (flushTimeout) {
      clearTimeout(flushTimeout);
    }
    flushEvents();
  }
}

// Отправка при закрытии/переходе страницы
if (typeof window !== 'undefined') {
  // При уходе со страницы - отправляем сразу через fetch с keepalive
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && eventQueue.length > 0) {
      const sessionId = getSessionId();
      const eventsWithSession = eventQueue.map(e => ({
        ...e,
        session_id: sessionId,
      }));
      eventQueue = [];

      // Используем fetch с keepalive вместо sendBeacon для правильных headers
      fetch(`${API_BASE}/analytics/track/batch/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ events: eventsWithSession }),
        keepalive: true, // Позволяет запросу завершиться даже после закрытия страницы
      }).catch(() => {
        // Fallback на sendBeacon с Blob для правильного Content-Type
        const blob = new Blob(
          [JSON.stringify({ events: eventsWithSession })],
          { type: 'application/json' }
        );
        navigator.sendBeacon(`${API_BASE}/analytics/track/batch/`, blob);
      });
    }
  });

  // Также при beforeunload
  window.addEventListener('beforeunload', () => {
    if (eventQueue.length > 0) {
      const sessionId = getSessionId();
      const eventsWithSession = eventQueue.map(e => ({
        ...e,
        session_id: sessionId,
      }));
      eventQueue = [];

      // sendBeacon с Blob для правильного Content-Type
      const blob = new Blob(
        [JSON.stringify({ events: eventsWithSession })],
        { type: 'application/json' }
      );
      navigator.sendBeacon(`${API_BASE}/analytics/track/batch/`, blob);
    }
  });
}

// ==================== Public API ====================

export const analytics = {
  /**
   * Открытие приложения
   */
  trackAppOpen(): void {
    queueEvent({ event_type: 'app_open' });
  },

  /**
   * Просмотр товара (открыл страницу)
   * Отправляется сразу, т.к. это важное событие
   */
  trackProductView(productId: number): void {
    queueEvent({
      event_type: 'product_view',
      product_id: productId,
    }, true); // immediate
  },

  /**
   * Клик на товар в каталоге
   * Отправляется сразу, т.к. пользователь переходит на другую страницу
   */
  trackProductClick(productId: number): void {
    queueEvent({
      event_type: 'product_click',
      product_id: productId,
    }, true); // immediate - важно отправить до перехода
  },

  /**
   * Добавление в корзину
   * Отправляется сразу - важное конверсионное событие
   */
  trackCartAdd(productId: number, quantity: number = 1): void {
    queueEvent({
      event_type: 'cart_add',
      product_id: productId,
      metadata: { quantity },
    }, true); // immediate
  },

  /**
   * Удаление из корзины
   */
  trackCartRemove(productId: number): void {
    queueEvent({
      event_type: 'cart_remove',
      product_id: productId,
    }, true); // immediate
  },

  /**
   * Просмотр категории
   */
  trackCategoryView(categoryId: number): void {
    queueEvent({
      event_type: 'category_view',
      category_id: categoryId,
    });
  },

  /**
   * Поисковый запрос
   */
  trackSearch(query: string): void {
    if (!query.trim()) return;
    queueEvent({
      event_type: 'search',
      search_query: query.trim(),
    });
  },

  /**
   * Начало оформления заказа
   */
  trackCheckoutStart(): void {
    queueEvent({ event_type: 'checkout_start' }, true); // immediate
  },

  /**
   * Заказ оформлен
   */
  trackOrderComplete(orderId: number, total: number): void {
    queueEvent({
      event_type: 'order_complete',
      metadata: { order_id: orderId, total },
    }, true); // immediate
  },

  /**
   * Принудительная отправка всех событий
   */
  flush: flushEvents,
};

export default analytics;
