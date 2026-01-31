// Shop types - соответствуют API бэкенда

export interface Category {
  id: number;
  title: string;
  slug: string;
  sort_order: number;
  products_count?: number;
}

export interface ProductImage {
  id: number;
  url: string;
  alt_text: string;
  is_main: boolean;
  sort_order: number;
}

export interface Product {
  id: number;
  title: string;
  slug: string;
  description?: string;
  price: number;  // копейки
  price_display: string;
  old_price?: number;
  old_price_display?: string;
  has_discount: boolean;
  qty_available?: number;
  is_unlimited?: boolean;
  is_available: boolean;
  main_image?: string;
  images?: ProductImage[];
  category_slug?: string;
  category?: {
    id: number;
    title: string;
    slug: string;
  };
  created_at?: string;
}

export interface CartItem {
  product_id: number;
  product: Product;
  quantity: number;
}

export interface PromoCode {
  code: string;
  discount_percent?: number;
  fixed_amount?: number;
  is_active: boolean;
  expires_at?: string;
}

// Order types
export type OrderStatus = 'new' | 'confirmed' | 'in_progress' | 'delivering' | 'done' | 'cancelled';
export type PaymentMethod = 'link_after_order';  // В будущем: 'card_online' | 'cash' | 'card_on_delivery'

export interface OrderItem {
  id: number;
  product_id?: number;
  product_title: string;
  qty: number;
  unit_price: number;
  unit_price_display: string;
  line_total: number;
  line_total_display: string;
  image_url?: string;
}

export interface Order {
  id: number;
  uid: string;
  status: OrderStatus;
  status_display: string;
  payment_method: PaymentMethod;
  payment_method_display: string;
  total: number;
  total_display: string;
  items_count: number;
  customer_name: string;
  created_at: string;
}

export interface OrderDetail extends Order {
  subtotal: number;
  subtotal_display: string;
  delivery_fee: number;
  delivery_fee_display: string;
  discount: number;
  discount_display: string;
  customer_phone: string;
  delivery_address: string;
  delivery_comment: string;
  delivery_date?: string;
  delivery_time_from?: string;
  delivery_time_to?: string;
  items: OrderItem[];
  updated_at: string;
}

export interface User {
  id: number;
  telegram_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

// API Request types
export interface ProductsFilter {
  category?: string;  // slug
  search?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  ordering?: string;
  page?: number;
}

export interface CheckoutData {
  customer_name: string;
  customer_phone: string;
  delivery_address: string;
  delivery_comment?: string;
  delivery_date?: string;
  delivery_time_from?: string;
  delivery_time_to?: string;
  payment_method: PaymentMethod;
  items: { product_id: number; qty: number }[];
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
