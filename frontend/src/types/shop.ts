// Shop types

export interface Category {
  id: string;
  title: string;
  slug: string;
  is_active: boolean;
  image_url?: string;
}

export interface Product {
  id: string;
  category_id: string;
  title: string;
  description: string;
  price: number;
  stock: number;
  is_active: boolean;
  image_url: string;
  images?: string[];
  is_new?: boolean;
  is_hit?: boolean;
  created_at: string;
}

export interface CartItem {
  product_id: string;
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

export interface Order {
  id: string;
  user_id: string;
  status: OrderStatus;
  total_amount: number;
  customer_name: string;
  phone: string;
  address: string;
  comment?: string;
  promo_code?: string;
  discount_amount?: number;
  created_at: string;
  items?: OrderItem[];
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  title_snapshot: string;
  price_snapshot: number;
  quantity: number;
  image_url?: string;
}

export type OrderStatus = 'created' | 'confirmed' | 'delivering' | 'done' | 'canceled';

export interface User {
  id: string;
  telegram_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  created_at: string;
}

// API types
export interface ProductsFilter {
  category_id?: string;
  search?: string;
  sort?: 'default' | 'new' | 'price_asc' | 'price_desc';
  limit?: number;
  offset?: number;
}

export interface CheckoutData {
  customer_name: string;
  phone: string;
  address: string;
  comment?: string;
  promo_code?: string;
}
