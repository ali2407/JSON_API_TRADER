"""Trade API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..database import get_db
from ..trading_service import trading_service

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.post("", response_model=schemas.Trade, status_code=201)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade"""
    db_trade = crud.create_trade(db=db, trade=trade)

    # Log trade created event
    crud.create_trade_event(
        db, db_trade.id,
        schemas.TradeEventType.TRADE_CREATED.value,
        {
            "symbol": trade.symbol,
            "direction": trade.direction.value,
            "margin_usd": trade.margin_usd,
            "entry_price": trade.entry_price,
            "stop_loss": trade.stop_loss,
            "entries_count": len(trade.entries),
            "take_profits_count": len(trade.take_profits),
        }
    )

    return db_trade


@router.get("", response_model=List[schemas.Trade])
def get_trades(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all trades with optional status filter"""
    return crud.get_trades(db=db, status=status, skip=skip, limit=limit)


@router.get("/summary", response_model=schemas.TradeSummary)
def get_trades_summary(db: Session = Depends(get_db)):
    """Get trade statistics summary for dashboard"""
    return crud.get_trades_summary(db=db)


@router.get("/{trade_id}", response_model=schemas.Trade)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a specific trade by ID"""
    db_trade = crud.get_trade(db=db, trade_id=trade_id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade


@router.patch("/{trade_id}", response_model=schemas.Trade)
def update_trade(
    trade_id: int,
    trade_update: schemas.TradeUpdate,
    db: Session = Depends(get_db)
):
    """Update a trade"""
    db_trade = crud.update_trade(db=db, trade_id=trade_id, trade_update=trade_update)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade


@router.delete("/{trade_id}", status_code=204)
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """Delete a trade"""
    success = crud.delete_trade(db=db, trade_id=trade_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trade not found")
    return None


@router.post("/{trade_id}/start", response_model=schemas.Trade)
async def start_trade(trade_id: int, db: Session = Depends(get_db)):
    """Start trade execution (place orders on exchange)"""
    db_trade = crud.get_trade(db=db, trade_id=trade_id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    if db_trade.status != "PENDING":
        raise HTTPException(status_code=400, detail="Trade already started")

    try:
        # Start trade with stored API keys
        await trading_service.start_trade(db, trade_id)

        # Get updated trade
        return crud.get_trade(db=db, trade_id=trade_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start trade: {str(e)}")


@router.post("/{trade_id}/close", response_model=schemas.Trade)
async def close_trade(trade_id: int, db: Session = Depends(get_db)):
    """Close trade position"""
    db_trade = crud.get_trade(db=db, trade_id=trade_id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    if db_trade.status == "CLOSED":
        raise HTTPException(status_code=400, detail="Trade already closed")

    try:
        # Close trade via trading service
        await trading_service.close_trade(db, trade_id)

        # Get updated trade
        return crud.get_trade(db=db, trade_id=trade_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close trade: {str(e)}")


@router.get("/{trade_id}/events", response_model=List[schemas.TradeEvent])
def get_trade_events(trade_id: int, db: Session = Depends(get_db)):
    """Get all events for a trade"""
    db_trade = crud.get_trade(db=db, trade_id=trade_id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    return crud.get_trade_events(db=db, trade_id=trade_id)
