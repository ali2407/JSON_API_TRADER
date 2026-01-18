"""Market data router for fetching OHLC/klines data"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio
import ccxt

router = APIRouter(prefix="/api/market", tags=["market"])

# Supported timeframes mapping
TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1D": "1d",
}

# Cached client for faster requests (avoid re-creating client and loading markets each time)
_cached_client: Optional[ccxt.bingx] = None
_markets_loaded: bool = False


async def get_cached_client() -> ccxt.bingx:
    """Get a cached public BingX client for market data"""
    global _cached_client, _markets_loaded

    if _cached_client is None:
        _cached_client = ccxt.bingx({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',
            }
        })

    if not _markets_loaded:
        await asyncio.to_thread(_cached_client.load_markets)
        _markets_loaded = True

    return _cached_client


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query("1h", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(500, description="Number of candles", ge=1, le=1500),
):
    """
    Fetch OHLC candlestick data for a symbol.

    Args:
        symbol: Trading pair (e.g., "BTC", "ETH", "SOL")
        interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
        limit: Number of candles to fetch (max 1500)

    Returns:
        List of candles: [timestamp, open, high, low, close, volume]
    """
    try:
        # Convert symbol to CCXT format
        base_symbol = symbol.upper().replace("USDT", "").replace("/", "")
        ccxt_symbol = f"{base_symbol}/USDT:USDT"

        # Map timeframe
        timeframe = TIMEFRAME_MAP.get(interval, "1h")

        # Get cached client (much faster after first request)
        client = await get_cached_client()

        # Fetch OHLCV data
        ohlcv = await asyncio.to_thread(
            client.fetch_ohlcv,
            ccxt_symbol,
            timeframe,
            limit=limit
        )

        # Convert to lightweight-charts format
        # [timestamp, open, high, low, close, volume] -> {time, open, high, low, close}
        candles = []
        for candle in ohlcv:
            candles.append({
                "time": int(candle[0] / 1000),  # Convert ms to seconds
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5] if len(candle) > 5 else 0,
            })

        return {
            "symbol": ccxt_symbol,
            "interval": timeframe,
            "candles": candles
        }

    except ccxt.BadSymbol:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch klines: {str(e)}")


@router.get("/price/{symbol}")
async def get_current_price(symbol: str):
    """
    Get current price for a symbol.

    Args:
        symbol: Trading pair (e.g., "BTC", "ETH")

    Returns:
        Current price data
    """
    try:
        # Convert symbol to CCXT format
        base_symbol = symbol.upper().replace("USDT", "").replace("/", "")
        ccxt_symbol = f"{base_symbol}/USDT:USDT"

        # Get cached client (much faster after first request)
        client = await get_cached_client()

        ticker = await asyncio.to_thread(
            client.fetch_ticker,
            ccxt_symbol
        )

        return {
            "symbol": ccxt_symbol,
            "price": ticker['last'],
            "high24h": ticker['high'],
            "low24h": ticker['low'],
            "change24h": ticker['percentage'],
            "volume24h": ticker['quoteVolume'],
        }

    except ccxt.BadSymbol:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price: {str(e)}")
