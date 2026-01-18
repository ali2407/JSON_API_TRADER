"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, enum.Enum):
    PENDING = "PENDING"  # Trade plan loaded but not started
    ACTIVE = "ACTIVE"    # Orders placed, waiting for fills
    OPEN = "OPEN"        # Position is open
    CLOSED = "CLOSED"    # Position fully closed


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)  # Unique identifier like "SOL-SHORT-3c0c976d1ea5"

    # Trade setup
    symbol = Column(String, index=True)
    direction = Column(String)  # LONG or SHORT
    status = Column(String, default=TradeStatus.PENDING.value)

    margin_usd = Column(Float)
    leverage = Column(String)
    entry_price = Column(Float)
    average_price = Column(Float, nullable=True)
    stop_loss = Column(Float)
    max_loss_percent = Column(Float, nullable=True)

    # Position state
    position_size = Column(Float, default=0)  # Current position size
    avg_entry = Column(Float, default=0)  # Actual average entry price
    current_sl_price = Column(Float, nullable=True)
    is_in_profit = Column(Boolean, default=False)

    # P&L
    unrealized_pnl = Column(Float, default=0)
    realized_pnl = Column(Float, default=0)
    mark_price = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Journal fields
    theory = Column(Text, nullable=True)  # Why the trade was taken
    setup_type = Column(String, nullable=True)  # e.g., "breakout", "support bounce"
    confidence_level = Column(Integer, nullable=True)  # 1-5 scale
    pre_trade_notes = Column(Text, nullable=True)
    post_trade_notes = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags

    # Relationships
    entries = relationship("OrderEntry", back_populates="trade", cascade="all, delete-orphan")
    take_profits = relationship("TakeProfit", back_populates="trade", cascade="all, delete-orphan")
    events = relationship("TradeEvent", back_populates="trade", cascade="all, delete-orphan")


class OrderEntry(Base):
    __tablename__ = "order_entries"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), index=True)

    label = Column(String)  # "Entry", "RB1", "RB2", etc.
    price = Column(Float)
    size_usd = Column(Float)
    average_after_fill = Column(Float)  # Expected average price after this fills

    filled = Column(Boolean, default=False)
    filled_at = Column(DateTime, nullable=True)
    order_id = Column(String, nullable=True)  # Exchange order ID

    trade = relationship("Trade", back_populates="entries")


class TakeProfit(Base):
    __tablename__ = "take_profits"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), index=True)

    level = Column(String)  # "TP1", "TP2", etc.
    price = Column(Float)
    size_percent = Column(Float)  # Percentage of position to close

    filled = Column(Boolean, default=False)
    filled_at = Column(DateTime, nullable=True)
    order_id = Column(String, nullable=True)  # Exchange order ID

    trade = relationship("Trade", back_populates="take_profits")


class TradeEvent(Base):
    __tablename__ = "trade_events"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), index=True)

    event_type = Column(String)  # ORDER_PLACED, ORDER_FILLED, SL_MOVED, TP_HIT, CLOSED, etc.
    event_data = Column(Text, nullable=True)  # JSON string with event details

    created_at = Column(DateTime, default=datetime.utcnow)

    trade = relationship("Trade", back_populates="events")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # User-friendly name like "BingX Main"
    exchange = Column(String, default="bingx")  # Exchange name

    api_key = Column(String)  # Encrypted API key
    api_secret = Column(String)  # Encrypted API secret

    # BTCC-specific: requires username/password login in addition to API keys
    btcc_username = Column(String, nullable=True)  # Encrypted BTCC username (email/phone)
    btcc_password = Column(String, nullable=True)  # Encrypted BTCC password

    testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)  # Can be disabled without deleting
    is_default = Column(Boolean, default=False)  # Default account for new trades

    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)
