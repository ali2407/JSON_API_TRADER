"""Sync service for reconciling trades with BingX exchange"""
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.bingx_client import BingXClient
from backend import models, crud, crud_apikeys, schemas
from backend.trading_service import trading_service

logger = logging.getLogger(__name__)


class SyncService:
    """Service to sync trades with BingX exchange"""

    def __init__(self):
        self.is_syncing = False
        self._sync_task: Optional[asyncio.Task] = None

    async def sync_all_trades(self, db: Session) -> dict:
        """
        Sync all active trades with BingX positions.

        Returns:
            Summary of sync results
        """
        if self.is_syncing:
            logger.warning("Sync already in progress, skipping")
            return {"status": "skipped", "reason": "sync_in_progress"}

        self.is_syncing = True
        results = {
            "synced": 0,
            "closed": 0,
            "errors": 0,
            "resumed": 0,
        }

        try:
            # Get all active/open trades
            active_trades = crud.get_trades(db, status=schemas.TradeStatus.ACTIVE)
            open_trades = crud.get_trades(db, status=schemas.TradeStatus.OPEN)
            all_active = active_trades + open_trades

            if not all_active:
                logger.info("No active trades to sync")
                return results

            logger.info(f"Syncing {len(all_active)} active trades...")

            for trade in all_active:
                try:
                    sync_result = await self.sync_trade(db, trade)
                    if sync_result.get("closed"):
                        results["closed"] += 1
                    if sync_result.get("resumed"):
                        results["resumed"] += 1
                    results["synced"] += 1
                except Exception as e:
                    logger.error(f"Error syncing trade {trade.id}: {e}")
                    results["errors"] += 1

            logger.info(f"Sync complete: {results}")
            return results

        finally:
            self.is_syncing = False

    async def sync_trade(self, db: Session, trade: models.Trade) -> dict:
        """
        Sync a single trade with BingX.

        Returns:
            Dict with sync status
        """
        result = {"closed": False, "resumed": False, "updated": False}

        # Get API credentials
        api_key_db = crud_apikeys.get_default_api_key(db)
        if not api_key_db:
            keys = crud_apikeys.get_api_keys(db, active_only=True)
            if not keys:
                logger.warning(f"No API keys available to sync trade {trade.id}")
                return result
            api_key_db = keys[0]

        credentials = crud_apikeys.get_decrypted_credentials(db, api_key_db.id)
        if not credentials:
            logger.warning(f"Failed to decrypt credentials for trade {trade.id}")
            return result

        # Initialize BingX client
        client = BingXClient(
            api_key=credentials['api_key'],
            api_secret=credentials['api_secret'],
            testnet=api_key_db.testnet
        )
        await client.initialize()

        # Format symbol for BingX
        symbol = trade.symbol
        if not symbol.endswith(":USDT"):
            # Convert to CCXT format if needed
            base = symbol.replace("/USDT", "").replace("USDT", "").replace("/", "")
            symbol = f"{base}/USDT:USDT"

        # Check if position exists on BingX
        position = await client.get_position(symbol)

        if not position or float(position.get('contracts', 0)) == 0:
            # No position on exchange - mark trade as closed
            logger.info(f"Trade {trade.id} ({trade.symbol}): No position on BingX, marking as CLOSED")

            crud.create_trade_event(
                db, trade.id,
                schemas.TradeEventType.TRADE_CLOSED.value,
                {"reason": "sync_no_position", "synced": True}
            )

            crud.update_trade(db, trade.id, schemas.TradeUpdate(
                status=schemas.TradeStatus.CLOSED
            ))

            result["closed"] = True
            return result

        # Position exists - update trade data
        logger.info(f"Trade {trade.id} ({trade.symbol}): Position found on BingX")

        # Update position info from exchange
        contracts = float(position.get('contracts', 0))
        entry_price = float(position.get('entryPrice', 0))
        unrealized_pnl = float(position.get('unrealizedPnl', 0))

        crud.update_trade(db, trade.id, schemas.TradeUpdate(
            position_size=contracts,
            avg_entry=entry_price if entry_price > 0 else None,
            unrealized_pnl=unrealized_pnl,
        ))
        result["updated"] = True

        # Check if monitoring is active, resume if not
        if trade.id not in trading_service.active_sessions:
            logger.info(f"Trade {trade.id}: Resuming monitoring...")
            await self.resume_monitoring(db, trade, client)
            result["resumed"] = True

        return result

    async def resume_monitoring(self, db: Session, trade: models.Trade, client: BingXClient):
        """Resume monitoring for an active trade"""
        try:
            from src.order_manager import OrderManager
            from src.strategy import TradingStrategy
            from src.models import TradePlan, TradeSetup, OrderEntry as SrcOrderEntry, TakeProfit as SrcTakeProfit

            # Convert DB trade to TradePlan
            trade_setup = TradeSetup(
                symbol=trade.symbol,
                direction=trade.direction,
                dateTime="",
                marginUSD=trade.margin_usd,
                entryPrice=trade.entry_price,
                averagePrice=trade.average_price or trade.entry_price,
                stopLoss=trade.stop_loss,
                leverage=trade.leverage,
                maxLossPercent=trade.max_loss_percent or 0,
            )

            order_entries = [
                SrcOrderEntry(
                    label=entry.label,
                    sizeUSD=entry.size_usd,
                    price=entry.price,
                    average=entry.average_after_fill,
                    filled=entry.filled,
                    order_id=entry.order_id,
                )
                for entry in trade.entries
            ]

            take_profits = [
                SrcTakeProfit(
                    level=tp.level,
                    price=tp.price,
                    sizePercent=tp.size_percent,
                    filled=tp.filled,
                    order_id=tp.order_id,
                )
                for tp in trade.take_profits
            ]

            trade_plan = TradePlan(
                tradeSetup=trade_setup,
                orderEntries=order_entries,
                takeProfits=take_profits,
                notes=trade.notes or "",
            )

            # Initialize order manager (don't place orders, just load state)
            order_manager = OrderManager(client, exchange="bingx")
            order_manager.load_trade_plan(trade_plan)

            # Reconstruct position state from DB
            filled_entries = [e.label for e in trade.entries if e.filled]
            filled_tps = [tp.level for tp in trade.take_profits if tp.filled]

            if filled_entries:
                # Position is open, update state
                order_manager.position_state.filled_entries = filled_entries
                order_manager.position_state.filled_tps = filled_tps
                order_manager.position_state.highest_tp_reached = len(filled_tps)

                if trade.avg_entry:
                    order_manager.position_state.average_entry = trade.avg_entry
                if trade.current_sl_price:
                    order_manager.position_state.current_sl_price = trade.current_sl_price

            # Initialize strategy for monitoring
            strategy = TradingStrategy(order_manager)

            # Store session
            trading_service.active_sessions[trade.id] = {
                "client": client,
                "order_manager": order_manager,
                "strategy": strategy,
                "trade_plan": trade_plan,
            }

            # Start monitoring in background
            asyncio.create_task(self._monitor_resumed_trade(db, trade.id))

            logger.info(f"Trade {trade.id}: Monitoring resumed successfully")

            crud.create_trade_event(
                db, trade.id,
                "MONITORING_RESUMED",
                {"filled_entries": filled_entries, "filled_tps": filled_tps}
            )

        except Exception as e:
            logger.error(f"Failed to resume monitoring for trade {trade.id}: {e}")
            raise

    async def _monitor_resumed_trade(self, db: Session, trade_id: int):
        """Background task to monitor a resumed trade"""
        if trade_id not in trading_service.active_sessions:
            return

        session = trading_service.active_sessions[trade_id]
        strategy = session["strategy"]

        try:
            await strategy.start_monitoring()
        except Exception as e:
            logger.error(f"Error monitoring resumed trade {trade_id}: {e}")
        finally:
            if trade_id in trading_service.active_sessions:
                del trading_service.active_sessions[trade_id]

    def start_periodic_sync(self, db_session_factory, interval: int = 30):
        """Start background periodic sync task"""
        if self._sync_task and not self._sync_task.done():
            logger.warning("Periodic sync already running")
            return

        async def periodic_sync():
            while True:
                await asyncio.sleep(interval)
                try:
                    db = db_session_factory()
                    await self.sync_all_trades(db)
                    db.close()
                except Exception as e:
                    logger.error(f"Periodic sync error: {e}")

        self._sync_task = asyncio.create_task(periodic_sync())
        logger.info(f"Started periodic sync (every {interval}s)")

    def stop_periodic_sync(self):
        """Stop the periodic sync task"""
        if self._sync_task:
            self._sync_task.cancel()
            self._sync_task = None
            logger.info("Stopped periodic sync")


# Global sync service instance
sync_service = SyncService()
