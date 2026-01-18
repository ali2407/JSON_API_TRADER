"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TradeDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


# APIKey schemas
class APIKeyBase(BaseModel):
    name: str
    exchange: str = "bingx"
    testnet: bool = True
    is_active: bool = True
    is_default: bool = False
    notes: Optional[str] = None


class APIKeyCreate(APIKeyBase):
    api_key: str
    api_secret: str
    # BTCC-specific credentials (required for BTCC exchange)
    btcc_username: Optional[str] = None  # Email or phone for BTCC login
    btcc_password: Optional[str] = None  # Password for BTCC login


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    notes: Optional[str] = None


class APIKeyValidate(BaseModel):
    """Schema for validating API key credentials"""
    api_key: str
    api_secret: str
    testnet: bool = False
    exchange: Optional[str] = "bingx"
    # BTCC-specific credentials
    btcc_username: Optional[str] = None
    btcc_password: Optional[str] = None


class APIKeyValidateResponse(BaseModel):
    """Response from API key validation"""
    valid: bool
    message: str
    balance: Optional[float] = None
    account_type: Optional[str] = None


class APIKey(APIKeyBase):
    id: int
    api_key_preview: str  # Only show first/last few chars
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# OrderEntry schemas
class OrderEntryBase(BaseModel):
    label: str
    price: float
    size_usd: float
    average_after_fill: float


class OrderEntryCreate(OrderEntryBase):
    pass


class OrderEntry(OrderEntryBase):
    id: int
    filled: bool = False
    filled_at: Optional[datetime] = None
    order_id: Optional[str] = None

    class Config:
        from_attributes = True


# TakeProfit schemas
class TakeProfitBase(BaseModel):
    level: str
    price: float
    size_percent: float


class TakeProfitCreate(TakeProfitBase):
    pass


class TakeProfit(TakeProfitBase):
    id: int
    filled: bool = False
    filled_at: Optional[datetime] = None
    order_id: Optional[str] = None

    class Config:
        from_attributes = True


# Trade schemas
class TradeBase(BaseModel):
    symbol: str
    direction: TradeDirection
    margin_usd: float
    leverage: str
    entry_price: float
    average_price: Optional[float] = None
    stop_loss: float
    max_loss_percent: Optional[float] = None
    notes: Optional[str] = None
    # Journal fields
    theory: Optional[str] = None
    setup_type: Optional[str] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)
    pre_trade_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TradeCreate(TradeBase):
    entries: List[OrderEntryCreate]
    take_profits: List[TakeProfitCreate]


class TradeUpdate(BaseModel):
    status: Optional[TradeStatus] = None
    position_size: Optional[float] = None
    avg_entry: Optional[float] = None
    current_sl_price: Optional[float] = None
    is_in_profit: Optional[bool] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    mark_price: Optional[float] = None
    # Journal updates
    theory: Optional[str] = None
    setup_type: Optional[str] = None
    confidence_level: Optional[int] = None
    pre_trade_notes: Optional[str] = None
    post_trade_notes: Optional[str] = None
    lessons_learned: Optional[str] = None
    tags: Optional[List[str]] = None


class Trade(TradeBase):
    id: int
    trade_id: str
    status: TradeStatus

    position_size: float = 0
    avg_entry: float = 0
    current_sl_price: Optional[float] = None
    is_in_profit: bool = False

    unrealized_pnl: float = 0
    realized_pnl: float = 0
    mark_price: Optional[float] = None

    # Additional journal fields
    post_trade_notes: Optional[str] = None
    lessons_learned: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    entries: List[OrderEntry] = []
    take_profits: List[TakeProfit] = []

    class Config:
        from_attributes = True


# Summary schemas for dashboard
class TradeSummary(BaseModel):
    total_trades: int
    pending: int
    active: int
    open: int
    closed: int
    total_unrealized_pnl: float
    total_realized_pnl: float


# TradeEvent schemas
class TradeEventType(str, Enum):
    TRADE_CREATED = "TRADE_CREATED"
    TRADE_STARTED = "TRADE_STARTED"
    ORDER_PLACED = "ORDER_PLACED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    SL_MOVED = "SL_MOVED"
    TP_HIT = "TP_HIT"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    TRADE_CLOSED = "TRADE_CLOSED"
    ERROR = "ERROR"


class TradeEventCreate(BaseModel):
    trade_id: int
    event_type: TradeEventType
    event_data: Optional[dict] = None


class TradeEvent(BaseModel):
    id: int
    trade_id: int
    event_type: str
    event_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
