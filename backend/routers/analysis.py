"""AI Analysis endpoints for trade insights"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..ai_analyzer import get_analyzer
from ..crud import get_trade, get_trades
from ..models import Trade

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class QuestionRequest(BaseModel):
    question: str


class AnalysisResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    analysis: Optional[str] = None
    insights: Optional[str] = None
    stats: Optional[dict] = None


@router.post("/trade/{trade_id}")
async def analyze_trade(trade_id: int, db: Session = Depends(get_db)):
    """Analyze a single trade using AI"""
    analyzer = get_analyzer()
    if not analyzer:
        raise HTTPException(status_code=503, detail="AI analyzer not available. Check OPENAI_API_KEY.")

    trade = get_trade(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Convert to dict for analysis
    trade_dict = {
        "trade_id": trade.trade_id,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "status": trade.status,
        "entry_price": trade.entry_price,
        "stop_loss": trade.stop_loss,
        "margin_usd": trade.margin_usd,
        "leverage": trade.leverage,
        "realized_pnl": trade.realized_pnl,
        "unrealized_pnl": trade.unrealized_pnl,
        "position_size": trade.position_size,
        "avg_entry": trade.avg_entry,
        "theory": trade.theory,
        "setup_type": trade.setup_type,
        "confidence_level": trade.confidence_level,
        "pre_trade_notes": trade.pre_trade_notes,
        "post_trade_notes": trade.post_trade_notes,
        "lessons_learned": trade.lessons_learned,
        "tags": trade.tags.split(",") if trade.tags else [],
        "take_profits": [{"level": tp.level, "filled": tp.filled} for tp in trade.take_profits],
        "entries": [{"label": e.label, "filled": e.filled} for e in trade.entries]
    }

    result = await analyzer.analyze_single_trade(trade_dict)
    return result


@router.post("/patterns")
async def find_patterns(db: Session = Depends(get_db)):
    """Find patterns across all trades"""
    analyzer = get_analyzer()
    if not analyzer:
        raise HTTPException(status_code=503, detail="AI analyzer not available. Check OPENAI_API_KEY.")

    trades = get_trades(db)
    if len(trades) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 trades for pattern analysis")

    # Convert to dicts
    trade_dicts = []
    for trade in trades:
        trade_dicts.append({
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "status": trade.status,
            "realized_pnl": trade.realized_pnl,
            "unrealized_pnl": trade.unrealized_pnl,
            "theory": trade.theory,
            "setup_type": trade.setup_type,
            "confidence_level": trade.confidence_level,
            "tags": trade.tags.split(",") if trade.tags else [],
            "take_profits": [{"level": tp.level, "filled": tp.filled} for tp in trade.take_profits]
        })

    result = await analyzer.find_patterns(trade_dicts)
    return result


@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Generate insights from trading history"""
    analyzer = get_analyzer()
    if not analyzer:
        raise HTTPException(status_code=503, detail="AI analyzer not available. Check OPENAI_API_KEY.")

    trades = get_trades(db)
    if not trades:
        raise HTTPException(status_code=400, detail="No trades to analyze")

    # Convert to dicts
    trade_dicts = []
    for trade in trades:
        trade_dicts.append({
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "status": trade.status,
            "realized_pnl": trade.realized_pnl,
            "unrealized_pnl": trade.unrealized_pnl,
            "setup_type": trade.setup_type,
            "confidence_level": trade.confidence_level,
            "take_profits": [{"level": tp.level, "filled": tp.filled} for tp in trade.take_profits]
        })

    result = await analyzer.generate_insights(trade_dicts)
    return result


@router.post("/ask")
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """Ask a question about trading history"""
    analyzer = get_analyzer()
    if not analyzer:
        raise HTTPException(status_code=503, detail="AI analyzer not available. Check OPENAI_API_KEY.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    trades = get_trades(db)

    # Convert to dicts
    trade_dicts = []
    for trade in trades:
        trade_dicts.append({
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "status": trade.status,
            "realized_pnl": trade.realized_pnl,
            "unrealized_pnl": trade.unrealized_pnl,
            "theory": trade.theory,
            "setup_type": trade.setup_type,
            "confidence_level": trade.confidence_level,
            "tags": trade.tags.split(",") if trade.tags else [],
            "created_at": str(trade.created_at)
        })

    result = await analyzer.ask_question(request.question, trade_dicts)
    return result
