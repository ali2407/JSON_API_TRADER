"""Trading service that connects stored API keys to exchange clients"""
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict
from sqlalchemy.orm import Session

# Add src to path for importing existing trading modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.bingx_client import BingXClient
from src.btcc_client import BTCCClient
from src.order_manager import OrderManager
from src.strategy import TradingStrategy
from src.models import TradePlan, TradeSetup, OrderEntry as SrcOrderEntry, TakeProfit as SrcTakeProfit

from . import models, crud, crud_apikeys, schemas


class TradingService:
    """Service to manage active trading sessions"""

    def __init__(self):
        self.active_sessions: Dict[int, dict] = {}  # trade_id -> session data

    async def start_trade(self, db: Session, trade_id: int) -> bool:
        """Start a trade with stored API keys"""
        # Get trade from database
        db_trade = crud.get_trade(db, trade_id)
        if not db_trade:
            raise ValueError(f"Trade {trade_id} not found")

        if db_trade.status != models.TradeStatus.PENDING.value:
            raise ValueError(f"Trade must be in PENDING status to start")

        # Get default API key or first active key
        api_key_db = crud_apikeys.get_default_api_key(db)
        if not api_key_db:
            # Try to get any active key
            keys = crud_apikeys.get_api_keys(db, active_only=True)
            if not keys:
                raise ValueError("No active API keys found. Please add an API key in Accounts.")
            api_key_db = keys[0]

        # Get decrypted credentials
        credentials = crud_apikeys.get_decrypted_credentials(db, api_key_db.id)
        if not credentials:
            raise ValueError("Failed to decrypt API credentials")

        api_key = credentials['api_key']
        api_secret = credentials['api_secret']

        # Initialize exchange client based on exchange type
        exchange = getattr(api_key_db, 'exchange', 'bingx') or 'bingx'

        if exchange == "btcc":
            # BTCC requires login with username/password
            btcc_username = credentials.get('btcc_username')
            btcc_password = credentials.get('btcc_password')

            if not btcc_username or not btcc_password:
                raise ValueError("BTCC requires username and password. Please update your API key settings.")

            client = BTCCClient(
                api_key=api_key,
                api_secret=api_secret,
                testnet=api_key_db.testnet
            )

            # Login to get authentication token
            await client.login(btcc_username, btcc_password)
            await client.initialize()
        else:  # Default to BingX
            client = BingXClient(
                api_key=api_key,
                api_secret=api_secret,
                testnet=api_key_db.testnet
            )
            await client.initialize()

        # Convert database trade to TradePlan model
        trade_plan = self._db_trade_to_trade_plan(db_trade)

        # Initialize order manager with exchange type for proper symbol formatting
        order_manager = OrderManager(client, exchange=exchange)
        order_manager.load_trade_plan(trade_plan)

        # Initialize trade (set leverage, place orders)
        await order_manager.initialize_trade()

        # Log trade started event
        crud.create_trade_event(
            db, trade_id,
            schemas.TradeEventType.TRADE_STARTED.value,
            {"api_key_name": api_key_db.name, "testnet": api_key_db.testnet, "exchange": exchange}
        )

        # Update trade status to ACTIVE
        crud.update_trade(db, trade_id, schemas.TradeUpdate(
            status=schemas.TradeStatus.ACTIVE
        ))

        # Start strategy monitoring in background
        strategy = TradingStrategy(order_manager)

        # Store session
        self.active_sessions[trade_id] = {
            "client": client,
            "order_manager": order_manager,
            "strategy": strategy,
            "trade_plan": trade_plan,
        }

        # Start monitoring task
        asyncio.create_task(self._monitor_trade(db, trade_id))

        return True

    async def _monitor_trade(self, db: Session, trade_id: int):
        """Monitor trade and update database"""
        if trade_id not in self.active_sessions:
            return

        session = self.active_sessions[trade_id]
        strategy = session["strategy"]
        order_manager = session["order_manager"]

        try:
            # Start strategy monitoring (this will run until trade is closed)
            await strategy.start_monitoring()
        except Exception as e:
            print(f"Error monitoring trade {trade_id}: {e}")
        finally:
            # Clean up session
            if trade_id in self.active_sessions:
                del self.active_sessions[trade_id]

    async def close_trade(self, db: Session, trade_id: int) -> bool:
        """Close a trade position"""
        if trade_id not in self.active_sessions:
            # Trade not actively running
            db_trade = crud.get_trade(db, trade_id)
            if db_trade:
                # Log trade closed event
                crud.create_trade_event(
                    db, trade_id,
                    schemas.TradeEventType.TRADE_CLOSED.value,
                    {"reason": "manual_close", "had_active_session": False}
                )
                crud.update_trade(db, trade_id, schemas.TradeUpdate(
                    status=schemas.TradeStatus.CLOSED
                ))
            return True

        session = self.active_sessions[trade_id]
        order_manager = session["order_manager"]
        strategy = session["strategy"]

        # Close position
        await order_manager.close_entire_position()

        # Stop monitoring
        strategy.stop_monitoring()

        # Log trade closed event
        crud.create_trade_event(
            db, trade_id,
            schemas.TradeEventType.TRADE_CLOSED.value,
            {"reason": "manual_close", "had_active_session": True}
        )

        # Update database
        crud.update_trade(db, trade_id, schemas.TradeUpdate(
            status=schemas.TradeStatus.CLOSED
        ))

        # Clean up session
        del self.active_sessions[trade_id]

        return True

    def _db_trade_to_trade_plan(self, db_trade: models.Trade) -> TradePlan:
        """Convert database trade model to TradePlan"""
        # Create trade setup
        trade_setup = TradeSetup(
            symbol=db_trade.symbol,
            direction=db_trade.direction,
            dateTime="",  # Not used in execution
            marginUSD=db_trade.margin_usd,
            entryPrice=db_trade.entry_price,
            averagePrice=db_trade.average_price or db_trade.entry_price,
            stopLoss=db_trade.stop_loss,
            leverage=db_trade.leverage,
            maxLossPercent=db_trade.max_loss_percent or 0,
        )

        # Create order entries
        order_entries = [
            SrcOrderEntry(
                label=entry.label,
                sizeUSD=entry.size_usd,
                price=entry.price,
                average=entry.average_after_fill,
            )
            for entry in db_trade.entries
        ]

        # Create take profits
        take_profits = [
            SrcTakeProfit(
                level=tp.level,
                price=tp.price,
                sizePercent=tp.size_percent,
            )
            for tp in db_trade.take_profits
        ]

        return TradePlan(
            tradeSetup=trade_setup,
            orderEntries=order_entries,
            takeProfits=take_profits,
            notes=db_trade.notes or "",
        )

    async def get_position_update(self, db: Session, trade_id: int) -> Optional[dict]:
        """Get current position state for a trade"""
        if trade_id not in self.active_sessions:
            return None

        session = self.active_sessions[trade_id]
        order_manager = session["order_manager"]
        position_state = order_manager.position_state

        if not position_state:
            return None

        return {
            "position_size": position_state.total_size_usd,
            "avg_entry": position_state.average_entry,
            "current_sl_price": position_state.current_sl_price,
            "is_in_profit": position_state.is_in_profit,
            "unrealized_pnl": 0,  # TODO: Calculate from position
            "realized_pnl": 0,    # TODO: Track realized PnL
        }


# Global trading service instance
trading_service = TradingService()
