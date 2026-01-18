"""Trading strategy logic - SL/TP management"""
import asyncio
import logging
from typing import Optional
from .order_manager import OrderManager
from .models import TradePlan, PositionState
from .config import Config

logger = logging.getLogger(__name__)


class TradingStrategy:
    """
    Manages the trading strategy:
    - Monitors position fills
    - Adjusts stop loss as entries fill
    - Moves SL to profit when TP1 hits
    - Cascades SL up as higher TPs hit
    """

    def __init__(self, order_manager: OrderManager):
        self.order_manager = order_manager
        self.client = order_manager.client
        self.running = False

    async def start_monitoring(self):
        """Start monitoring the position"""
        self.running = True
        logger.info("Started position monitoring")

        try:
            while self.running:
                await self._check_orders_and_adjust()
                await asyncio.sleep(2)  # Check every 2 seconds

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            raise

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Stopped position monitoring")

    async def _check_orders_and_adjust(self):
        """Check order status and adjust SL/TP accordingly"""
        trade_plan = self.order_manager.trade_plan
        position_state = self.order_manager.position_state

        if not trade_plan or not position_state:
            return

        # Check entry/rebuy orders
        await self._check_entry_fills()

        # Check take profit hits
        await self._check_tp_fills()

        # Check if position still exists
        await self._check_position_status()

    async def _check_entry_fills(self):
        """Check if any entry/rebuy orders have filled"""
        trade_plan = self.order_manager.trade_plan
        position_state = self.order_manager.position_state

        for entry in trade_plan.orderEntries:
            if entry.filled or not entry.order_id:
                continue

            # Check order status
            try:
                order = await self.client.get_order(
                    entry.order_id,
                    self.order_manager.symbol_formatted
                )

                if order['status'] == 'closed' or order['status'] == 'filled':
                    logger.info(f"✓ {entry.label} filled @ {entry.price}")

                    # Mark as filled
                    entry.filled = True
                    position_state.filled_entries.append(entry.label)

                    # Update position state
                    position_state.update_average_entry(entry.price, entry.sizeUSD)

                    # Update stop loss to cover new position size
                    await self._update_sl_for_position()

                    # If this is the first entry, place TP orders
                    if len(position_state.filled_entries) == 1:
                        logger.info("First entry filled - placing TP orders")
                        await self.order_manager.place_take_profit_orders()

            except Exception as e:
                logger.error(f"Error checking {entry.label} order: {e}")

    async def _check_tp_fills(self):
        """Check if any TP orders have filled"""
        trade_plan = self.order_manager.trade_plan
        position_state = self.order_manager.position_state

        for idx, tp in enumerate(trade_plan.takeProfits):
            if tp.filled or not tp.order_id:
                continue

            try:
                order = await self.client.get_order(
                    tp.order_id,
                    self.order_manager.symbol_formatted
                )

                if order['status'] == 'closed' or order['status'] == 'filled':
                    logger.info(f"✓ {tp.level} hit @ {tp.price}")

                    # Mark as filled
                    tp.filled = True
                    position_state.filled_tps.append(tp.level)
                    position_state.highest_tp_reached = idx + 1

                    # Move SL based on which TP was hit
                    await self._move_sl_to_profit(idx)

            except Exception as e:
                logger.error(f"Error checking {tp.level} order: {e}")

    async def _update_sl_for_position(self):
        """Update SL to cover entire position size"""
        position_state = self.order_manager.position_state
        trade_plan = self.order_manager.trade_plan

        # Get current position
        position = await self.client.get_position(self.order_manager.symbol_formatted)
        if not position:
            logger.warning("No position found")
            return

        total_contracts = float(position.get('contracts', 0))
        if total_contracts == 0:
            return

        # Use initial SL price from trade plan
        sl_price = trade_plan.tradeSetup.stopLoss

        # Update SL order
        await self.order_manager.update_stop_loss(sl_price, total_contracts)

        logger.info(
            f"Updated SL for {len(position_state.filled_entries)} entries: "
            f"{total_contracts} contracts @ {sl_price}"
        )

    async def _move_sl_to_profit(self, tp_index: int):
        """
        Move stop loss to profit after TP hit

        Args:
            tp_index: Index of TP that was hit (0-based)
        """
        trade_plan = self.order_manager.trade_plan
        position_state = self.order_manager.position_state
        setup = trade_plan.tradeSetup

        # Calculate new SL price based on which TP was hit
        if tp_index == 0:
            # TP1 hit - move SL just above entry
            base_price = setup.entryPrice
        else:
            # Higher TP hit - move SL just above previous TP
            base_price = trade_plan.takeProfits[tp_index - 1].price

        # Calculate SL offset (slightly above/below depending on direction)
        offset_multiplier = 1 + (Config.SL_OFFSET_PERCENT / 100)

        if setup.direction == "LONG":
            # For LONG, SL goes above (higher price)
            new_sl_price = base_price * offset_multiplier
        else:
            # For SHORT, SL goes below (lower price)
            new_sl_price = base_price / offset_multiplier

        # Format price
        new_sl_price = self.client.format_price(
            self.order_manager.symbol_formatted,
            new_sl_price
        )

        # Get remaining position size
        position = await self.client.get_position(self.order_manager.symbol_formatted)
        if not position:
            logger.warning("No position found")
            return

        remaining_contracts = float(position.get('contracts', 0))

        # Update SL
        await self.order_manager.update_stop_loss(new_sl_price, remaining_contracts)

        # Mark position as in profit
        position_state.is_in_profit = True

        logger.info(
            f"🎯 Moved SL to PROFIT: {new_sl_price} "
            f"(after {trade_plan.takeProfits[tp_index].level})"
        )

    async def _check_position_status(self):
        """Check if position still exists (may have hit SL)"""
        position = await self.client.get_position(self.order_manager.symbol_formatted)

        if not position or float(position.get('contracts', 0)) == 0:
            # Position closed - stop monitoring
            if self.order_manager.position_state.total_size_usd > 0:
                logger.info("Position closed - stopping monitoring")
                self.stop_monitoring()
