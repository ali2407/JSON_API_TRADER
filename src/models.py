"""Data models for trade plans and positions"""
from pydantic import BaseModel, Field, validator
from typing import List, Literal
from datetime import datetime


class TradeSetup(BaseModel):
    """Main trade setup configuration"""
    symbol: str
    direction: Literal["LONG", "SHORT"]
    dateTime: str
    marginUSD: float = Field(gt=0)
    entryPrice: float = Field(gt=0)
    averagePrice: float = Field(gt=0)
    stopLoss: float = Field(gt=0)
    leverage: str
    maxLossPercent: float = Field(ge=0, le=100)

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper()

    @property
    def leverage_value(self) -> int:
        """Extract numeric leverage value"""
        return int(self.leverage.replace('x', '').replace('X', ''))


class OrderEntry(BaseModel):
    """Individual order entry (Entry or Rebuy)"""
    label: str
    sizeUSD: float = Field(gt=0)
    price: float = Field(gt=0)
    average: float = Field(gt=0)

    # Runtime fields (not in JSON)
    filled: bool = False
    order_id: str = None


class TakeProfit(BaseModel):
    """Take profit level"""
    level: str
    price: float = Field(gt=0)
    sizePercent: float = Field(ge=0, le=100)

    # Runtime fields
    filled: bool = False
    order_id: str = None


class TradePlan(BaseModel):
    """Complete trade plan from JSON"""
    tradeSetup: TradeSetup
    orderEntries: List[OrderEntry]
    takeProfits: List[TakeProfit]
    notes: str = ""

    @validator('orderEntries')
    def must_have_entries(cls, v):
        if len(v) == 0:
            raise ValueError("Must have at least one order entry")
        return v

    @validator('takeProfits')
    def must_have_take_profits(cls, v):
        if len(v) == 0:
            raise ValueError("Must have at least one take profit level")
        return v


class PositionState(BaseModel):
    """Current state of the active position"""
    symbol: str
    direction: Literal["LONG", "SHORT"]
    total_size_usd: float = 0
    average_entry: float = 0
    filled_entries: List[str] = Field(default_factory=list)
    filled_tps: List[str] = Field(default_factory=list)
    current_sl_price: float = 0
    current_sl_order_id: str = None
    is_in_profit: bool = False
    highest_tp_reached: int = 0

    def update_average_entry(self, new_price: float, new_size_usd: float):
        """Update average entry price when a new order fills"""
        total_value = (self.average_entry * self.total_size_usd) + (new_price * new_size_usd)
        self.total_size_usd += new_size_usd
        self.average_entry = total_value / self.total_size_usd if self.total_size_usd > 0 else 0
