"""CRUD operations for database"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid

from . import models, schemas


def generate_trade_id(symbol: str, direction: str) -> str:
    """Generate unique trade ID like SOL-SHORT-3c0c976d1ea5"""
    short_uuid = str(uuid.uuid4())[:12]
    return f"{symbol}-{direction}-{short_uuid}"


# Trade CRUD operations
def create_trade(db: Session, trade: schemas.TradeCreate) -> models.Trade:
    """Create a new trade"""
    # Generate trade ID
    trade_id = generate_trade_id(trade.symbol, trade.direction.value)

    # Create trade
    db_trade = models.Trade(
        trade_id=trade_id,
        symbol=trade.symbol,
        direction=trade.direction.value,
        status=models.TradeStatus.PENDING.value,
        margin_usd=trade.margin_usd,
        leverage=trade.leverage,
        entry_price=trade.entry_price,
        average_price=trade.average_price,
        stop_loss=trade.stop_loss,
        max_loss_percent=trade.max_loss_percent,
        notes=trade.notes,
    )
    db.add(db_trade)
    db.flush()  # Get the trade.id

    # Create entries
    for entry in trade.entries:
        db_entry = models.OrderEntry(
            trade_id=db_trade.id,
            label=entry.label,
            price=entry.price,
            size_usd=entry.size_usd,
            average_after_fill=entry.average_after_fill,
        )
        db.add(db_entry)

    # Create take profits
    for tp in trade.take_profits:
        db_tp = models.TakeProfit(
            trade_id=db_trade.id,
            level=tp.level,
            price=tp.price,
            size_percent=tp.size_percent,
        )
        db.add(db_tp)

    db.commit()
    db.refresh(db_trade)
    return db_trade


def get_trade(db: Session, trade_id: int) -> Optional[models.Trade]:
    """Get trade by ID"""
    return db.query(models.Trade).filter(models.Trade.id == trade_id).first()


def get_trade_by_trade_id(db: Session, trade_id: str) -> Optional[models.Trade]:
    """Get trade by trade_id string"""
    return db.query(models.Trade).filter(models.Trade.trade_id == trade_id).first()


def get_trades(
    db: Session,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Trade]:
    """Get all trades with optional filtering"""
    query = db.query(models.Trade)

    if status:
        query = query.filter(models.Trade.status == status)

    return query.order_by(models.Trade.created_at.desc()).offset(skip).limit(limit).all()


def update_trade(db: Session, trade_id: int, trade_update: schemas.TradeUpdate) -> Optional[models.Trade]:
    """Update trade"""
    db_trade = get_trade(db, trade_id)
    if not db_trade:
        return None

    update_data = trade_update.model_dump(exclude_unset=True)

    # Update started_at if status changes to ACTIVE
    if "status" in update_data:
        if update_data["status"] == models.TradeStatus.ACTIVE.value and not db_trade.started_at:
            db_trade.started_at = datetime.utcnow()
        elif update_data["status"] == models.TradeStatus.CLOSED.value and not db_trade.closed_at:
            db_trade.closed_at = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_trade, key, value)

    db_trade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_trade)
    return db_trade


def delete_trade(db: Session, trade_id: int) -> bool:
    """Delete trade"""
    db_trade = get_trade(db, trade_id)
    if not db_trade:
        return False

    db.delete(db_trade)
    db.commit()
    return True


def update_order_entry(db: Session, entry_id: int, filled: bool, order_id: Optional[str] = None) -> Optional[models.OrderEntry]:
    """Update order entry fill status"""
    db_entry = db.query(models.OrderEntry).filter(models.OrderEntry.id == entry_id).first()
    if not db_entry:
        return None

    db_entry.filled = filled
    if filled:
        db_entry.filled_at = datetime.utcnow()
    if order_id:
        db_entry.order_id = order_id

    db.commit()
    db.refresh(db_entry)
    return db_entry


def update_take_profit(db: Session, tp_id: int, filled: bool, order_id: Optional[str] = None) -> Optional[models.TakeProfit]:
    """Update take profit fill status"""
    db_tp = db.query(models.TakeProfit).filter(models.TakeProfit.id == tp_id).first()
    if not db_tp:
        return None

    db_tp.filled = filled
    if filled:
        db_tp.filled_at = datetime.utcnow()
    if order_id:
        db_tp.order_id = order_id

    db.commit()
    db.refresh(db_tp)
    return db_tp


# Trade Event CRUD operations
def create_trade_event(
    db: Session,
    trade_id: int,
    event_type: str,
    event_data: Optional[dict] = None
) -> models.TradeEvent:
    """Create a trade event"""
    import json
    db_event = models.TradeEvent(
        trade_id=trade_id,
        event_type=event_type,
        event_data=json.dumps(event_data) if event_data else None,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_trade_events(
    db: Session,
    trade_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.TradeEvent]:
    """Get all events for a trade"""
    return db.query(models.TradeEvent).filter(
        models.TradeEvent.trade_id == trade_id
    ).order_by(models.TradeEvent.created_at.asc()).offset(skip).limit(limit).all()


def get_trades_summary(db: Session) -> schemas.TradeSummary:
    """Get summary statistics for dashboard"""
    total_trades = db.query(func.count(models.Trade.id)).scalar() or 0

    pending = db.query(func.count(models.Trade.id)).filter(
        models.Trade.status == models.TradeStatus.PENDING.value
    ).scalar() or 0

    active = db.query(func.count(models.Trade.id)).filter(
        models.Trade.status == models.TradeStatus.ACTIVE.value
    ).scalar() or 0

    open_count = db.query(func.count(models.Trade.id)).filter(
        models.Trade.status == models.TradeStatus.OPEN.value
    ).scalar() or 0

    closed = db.query(func.count(models.Trade.id)).filter(
        models.Trade.status == models.TradeStatus.CLOSED.value
    ).scalar() or 0

    # Sum unrealized PnL for open positions
    total_unrealized = db.query(func.sum(models.Trade.unrealized_pnl)).filter(
        models.Trade.status.in_([models.TradeStatus.ACTIVE.value, models.TradeStatus.OPEN.value])
    ).scalar() or 0.0

    # Sum realized PnL for all trades
    total_realized = db.query(func.sum(models.Trade.realized_pnl)).scalar() or 0.0

    return schemas.TradeSummary(
        total_trades=total_trades,
        pending=pending,
        active=active,
        open=open_count,
        closed=closed,
        total_unrealized_pnl=total_unrealized,
        total_realized_pnl=total_realized,
    )
