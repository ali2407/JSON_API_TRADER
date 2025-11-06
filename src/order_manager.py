"""Order execution and management engine"""
import asyncio
import logging
from typing import Dict, List, Optional
from .bingx_client import BingXClient
from .models import TradePlan, OrderEntry, TakeProfit, PositionState

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages order execution and position tracking"""

    def __init__(self, client: BingXClient):
        self.client = client
        self.trade_plan: Optional[TradePlan] = None
        self.position_state: Optional[PositionState] = None
        self.symbol_ccxt: Optional[str] = None

    def load_trade_plan(self, trade_plan: TradePlan):
        """Load a trade plan for execution"""
        self.trade_plan = trade_plan

        # Convert symbol to CCXT format (e.g., VET -> VET/USDT:USDT)
        symbol = trade_plan.tradeSetup.symbol
        self.symbol_ccxt = f"{symbol}/USDT:USDT"

        # Initialize position state
        self.position_state = PositionState(
            symbol=self.symbol_ccxt,
            direction=trade_plan.tradeSetup.direction,
            current_sl_price=trade_plan.tradeSetup.stopLoss
        )

        logger.info(f"Loaded trade plan for {symbol} {trade_plan.tradeSetup.direction}")

    async def initialize_trade(self) -> bool:
        """
        Initialize the trade by:
        1. Setting leverage
        2. Placing all entry/rebuy limit orders

        Returns:
            True if successful
        """
        if not self.trade_plan:
            raise ValueError("No trade plan loaded")

        setup = self.trade_plan.tradeSetup

        try:
            # Set leverage
            await self.client.set_leverage(
                self.symbol_ccxt,
                setup.leverage_value
            )

            # Place all entry/rebuy orders
            await self._place_entry_orders()

            logger.info("Trade initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize trade: {e}")
            raise

    async def _place_entry_orders(self):
        """Place all entry and rebuy limit orders"""
        setup = self.trade_plan.tradeSetup
        direction = setup.direction

        for entry in self.trade_plan.orderEntries:
            try:
                # Calculate position size in contracts
                position_size = self.client.calculate_position_size(
                    self.symbol_ccxt,
                    entry.sizeUSD,
                    entry.price,
                    setup.leverage_value
                )

                # Determine order side
                # LONG = buy, SHORT = sell
                side = "buy" if direction == "LONG" else "sell"

                # Place limit order
                order = await self.client.create_limit_order(
                    symbol=self.symbol_ccxt,
                    side=side,
                    amount=position_size,
                    price=entry.price
                )

                # Store order ID
                entry.order_id = order['id']

                logger.info(
                    f"Placed {entry.label} order: {position_size} @ {entry.price} (ID: {order['id']})"
                )

            except Exception as e:
                logger.error(f"Failed to place {entry.label} order: {e}")
                raise

    async def update_stop_loss(self, new_sl_price: float, position_size: Optional[float] = None):
        """
        Update stop loss order

        Args:
            new_sl_price: New stop loss price
            position_size: Position size to protect (None = use current position)
        """
        if not self.position_state:
            raise ValueError("Position state not initialized")

        # Cancel existing SL order if any
        if self.position_state.current_sl_order_id:
            try:
                await self.client.cancel_order(
                    self.position_state.current_sl_order_id,
                    self.symbol_ccxt
                )
                logger.info(f"Cancelled old SL order {self.position_state.current_sl_order_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel old SL order: {e}")

        # Determine position size
        if position_size is None:
            # Get current position from exchange
            position = await self.client.get_position(self.symbol_ccxt)
            if position:
                position_size = float(position.get('contracts', 0))
            else:
                position_size = self.position_state.total_size_usd / self.position_state.average_entry

        if position_size == 0:
            logger.warning("Position size is 0, not placing SL order")
            return

        # Determine SL order side (opposite of position direction)
        # LONG position = sell SL, SHORT position = buy SL
        sl_side = "sell" if self.trade_plan.tradeSetup.direction == "LONG" else "buy"

        try:
            # Place new stop loss order
            order = await self.client.create_stop_loss_order(
                symbol=self.symbol_ccxt,
                side=sl_side,
                amount=position_size,
                stop_price=new_sl_price
            )

            # Update position state
            self.position_state.current_sl_price = new_sl_price
            self.position_state.current_sl_order_id = order['id']

            logger.info(f"Updated SL to {new_sl_price} (ID: {order['id']})")

        except Exception as e:
            logger.error(f"Failed to update stop loss: {e}")
            raise

    async def place_take_profit_orders(self):
        """Place all take profit limit orders"""
        if not self.trade_plan:
            raise ValueError("No trade plan loaded")

        setup = self.trade_plan.tradeSetup
        direction = setup.direction

        # Get current position to calculate TP sizes
        position = await self.client.get_position(self.symbol_ccxt)
        if not position:
            logger.warning("No position found, cannot place TP orders")
            return

        total_contracts = float(position.get('contracts', 0))

        for tp in self.trade_plan.takeProfits:
            if tp.sizePercent == 0:
                logger.info(f"Skipping {tp.level} with 0% size")
                continue

            try:
                # Calculate TP size
                tp_size = total_contracts * (tp.sizePercent / 100.0)
                tp_size = self.client.format_amount(self.symbol_ccxt, tp_size)

                # Determine order side (opposite of entry)
                # LONG position = sell TP, SHORT position = buy TP
                side = "sell" if direction == "LONG" else "buy"

                # Place TP limit order with reduceOnly
                order = await self.client.create_limit_order(
                    symbol=self.symbol_ccxt,
                    side=side,
                    amount=tp_size,
                    price=tp.price,
                    params={'reduceOnly': True}
                )

                tp.order_id = order['id']

                logger.info(
                    f"Placed {tp.level} order: {tp_size} @ {tp.price} ({tp.sizePercent}%)"
                )

            except Exception as e:
                logger.error(f"Failed to place {tp.level} order: {e}")
                # Don't raise - continue with other TPs

    async def cancel_all_orders(self, symbol: Optional[str] = None):
        """Cancel all open orders for the symbol"""
        try:
            symbol = symbol or self.symbol_ccxt
            orders = await self.client.get_open_orders(symbol)

            for order in orders:
                try:
                    await self.client.cancel_order(order['id'], symbol)
                    logger.info(f"Cancelled order {order['id']}")
                except Exception as e:
                    logger.error(f"Failed to cancel order {order['id']}: {e}")

        except Exception as e:
            logger.error(f"Failed to cancel all orders: {e}")
            raise

    async def close_entire_position(self):
        """Close the entire position immediately"""
        try:
            await self.client.close_position(self.symbol_ccxt)
            logger.info(f"Closed entire position for {self.symbol_ccxt}")
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            raise
