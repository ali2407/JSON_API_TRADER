export enum TradeDirection {
  LONG = "LONG",
  SHORT = "SHORT",
}

export enum TradeStatus {
  PENDING = "PENDING",
  ACTIVE = "ACTIVE",
  OPEN = "OPEN",
  CLOSED = "CLOSED",
}

export interface OrderEntry {
  id: number;
  label: string;
  price: number;
  size_usd: number;
  average_after_fill: number;
  filled: boolean;
  filled_at: string | null;
  order_id: string | null;
}

export interface TakeProfit {
  id: number;
  level: string;
  price: number;
  size_percent: number;
  filled: boolean;
  filled_at: string | null;
  order_id: string | null;
}

export interface Trade {
  id: number;
  trade_id: string;
  symbol: string;
  direction: TradeDirection;
  status: TradeStatus;

  margin_usd: number;
  leverage: string;
  entry_price: number;
  average_price: number | null;
  stop_loss: number;
  max_loss_percent: number | null;

  position_size: number;
  avg_entry: number;
  current_sl_price: number | null;
  is_in_profit: boolean;

  unrealized_pnl: number;
  realized_pnl: number;
  mark_price: number | null;

  created_at: string;
  updated_at: string;
  started_at: string | null;
  closed_at: string | null;

  notes: string | null;

  // Journal fields
  theory: string | null;
  setup_type: string | null;
  confidence_level: number | null;
  pre_trade_notes: string | null;
  post_trade_notes: string | null;
  lessons_learned: string | null;
  tags: string[] | null;

  entries: OrderEntry[];
  take_profits: TakeProfit[];
}

export interface TradeSummary {
  total_trades: number;
  pending: number;
  active: number;
  open: number;
  closed: number;
  total_unrealized_pnl: number;
  total_realized_pnl: number;
}

export interface TradeCreate {
  symbol: string;
  direction: TradeDirection;
  margin_usd: number;
  leverage: string;
  entry_price: number;
  average_price?: number;
  stop_loss: number;
  max_loss_percent?: number;
  notes?: string;
  // Journal fields
  theory?: string;
  setup_type?: string;
  confidence_level?: number;
  pre_trade_notes?: string;
  tags?: string[];
  entries: Omit<OrderEntry, 'id' | 'filled' | 'filled_at' | 'order_id'>[];
  take_profits: Omit<TakeProfit, 'id' | 'filled' | 'filled_at' | 'order_id'>[];
}

// API Key types
export interface APIKey {
  id: number;
  name: string;
  exchange: string;
  api_key_preview: string;
  testnet: boolean;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  last_used_at: string | null;
  notes: string | null;
}

export interface APIKeyCreate {
  name: string;
  exchange?: string;
  api_key: string;
  api_secret: string;
  // BTCC-specific credentials
  btcc_username?: string;
  btcc_password?: string;
  testnet?: boolean;
  is_active?: boolean;
  is_default?: boolean;
  notes?: string;
}

export interface APIKeyValidate {
  api_key: string;
  api_secret: string;
  testnet: boolean;
  exchange?: string;
  // BTCC-specific credentials
  btcc_username?: string;
  btcc_password?: string;
}

export interface APIKeyValidateResponse {
  valid: boolean;
  message: string;
  balance: number | null;
  account_type: string | null;
}

export enum TradeEventType {
  TRADE_CREATED = "TRADE_CREATED",
  TRADE_STARTED = "TRADE_STARTED",
  ORDER_PLACED = "ORDER_PLACED",
  ORDER_FILLED = "ORDER_FILLED",
  ORDER_CANCELLED = "ORDER_CANCELLED",
  SL_MOVED = "SL_MOVED",
  TP_HIT = "TP_HIT",
  POSITION_OPENED = "POSITION_OPENED",
  POSITION_CLOSED = "POSITION_CLOSED",
  TRADE_CLOSED = "TRADE_CLOSED",
  ERROR = "ERROR",
}

export interface TradeEvent {
  id: number;
  trade_id: number;
  event_type: TradeEventType;
  event_data: string | null;
  created_at: string;
}

export interface AnalysisResponse {
  success: boolean;
  error?: string;
  analysis?: string;
  insights?: string;
  answer?: string;
  question?: string;
  stats?: {
    total_trades?: number;
    closed_trades?: number;
    tp_hit_rates?: Record<string, string>;
    setup_performance?: Record<string, { trades: number; pnl: number; wins: number }>;
  };
  trade_count?: number;
  wins?: number;
  losses?: number;
  win_rate?: string;
  total_pnl?: number;
  model?: string;
}
