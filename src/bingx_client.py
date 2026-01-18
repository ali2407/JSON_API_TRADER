"""BingX API client wrapper"""
import ccxt
import asyncio
from typing import Dict, List, Optional, Literal
from decimal import Decimal, ROUND_DOWN
import logging

logger = logging.getLogger(__name__)


class BingXClient:
    """Wrapper for BingX exchange API using CCXT"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize BingX client

        Args:
            api_key: BingX API key
            api_secret: BingX API secret
            testnet: Use testnet if True
        """
        self.exchange = ccxt.bingx({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Perpetual futures
            }
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)

        self.markets = None
        self.precision_cache = {}

    async def initialize(self):
        """Load markets and initialize client"""
        try:
            self.markets = await asyncio.to_thread(self.exchange.load_markets)
            logger.info(f"Loaded {len(self.markets)} markets from BingX")
        except Exception as e:
            logger.error(f"Failed to initialize BingX client: {e}")
            raise

    def get_precision(self, symbol: str) -> Dict:
        """Get price and amount precision for symbol"""
        if symbol not in self.precision_cache:
            market = self.markets.get(symbol)
            if not market:
                raise ValueError(f"Market {symbol} not found")

            self.precision_cache[symbol] = {
                'price': market['precision']['price'],
                'amount': market['precision']['amount'],
            }

        return self.precision_cache[symbol]

    def format_price(self, symbol: str, price: float) -> float:
        """Format price according to symbol precision"""
        precision = self.get_precision(symbol)
        price_precision = precision['price']

        if price_precision is not None:
            return float(Decimal(str(price)).quantize(
                Decimal(str(10 ** -price_precision)),
                rounding=ROUND_DOWN
            ))
        return price

    def format_amount(self, symbol: str, amount: float) -> float:
        """Format amount according to symbol precision"""
        precision = self.get_precision(symbol)
        amount_precision = precision['amount']

        if amount_precision is not None:
            return float(Decimal(str(amount)).quantize(
                Decimal(str(10 ** -amount_precision)),
                rounding=ROUND_DOWN
            ))
        return amount

    async def set_margin_mode(self, symbol: str, margin_mode: Literal["isolated", "cross"] = "isolated"):
        """
        Set margin mode for symbol

        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
            margin_mode: 'isolated' or 'cross'
        """
        try:
            result = await asyncio.to_thread(
                self.exchange.set_margin_mode,
                margin_mode,
                symbol
            )
            logger.info(f"Set margin mode to {margin_mode} for {symbol}")
            return result
        except Exception as e:
            # BingX may return error if mode is already set
            if "already" in str(e).lower() or "same" in str(e).lower():
                logger.info(f"Margin mode already {margin_mode} for {symbol}")
                return None
            logger.error(f"Failed to set margin mode: {e}")
            raise

    async def set_leverage(self, symbol: str, leverage: int, side: Literal["LONG", "SHORT", "BOTH"] = "BOTH"):
        """
        Set leverage for symbol

        Args:
            symbol: Trading symbol
            leverage: Leverage value
            side: Position side - LONG, SHORT, or BOTH (default)
        """
        try:
            result = await asyncio.to_thread(
                self.exchange.set_leverage,
                leverage,
                symbol,
                {"side": side}
            )
            logger.info(f"Set leverage to {leverage}x for {symbol} (side={side})")
            return result
        except Exception as e:
            logger.error(f"Failed to set leverage: {e}")
            raise

    async def create_limit_order(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        amount: float,
        price: float,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Create a limit order

        Args:
            symbol: Trading symbol (e.g., 'VET/USDT:USDT')
            side: 'buy' or 'sell'
            amount: Order amount in contracts
            price: Limit price
            params: Additional parameters

        Returns:
            Order response from exchange
        """
        try:
            formatted_price = self.format_price(symbol, price)
            formatted_amount = self.format_amount(symbol, amount)

            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'limit',
                side,
                formatted_amount,
                formatted_price,
                params or {}
            )

            logger.info(
                f"Created {side} limit order: {formatted_amount} {symbol} @ {formatted_price}"
            )
            return order

        except Exception as e:
            logger.error(f"Failed to create limit order: {e}")
            raise

    async def create_stop_loss_order(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        amount: float,
        stop_price: float,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Create a stop-loss order

        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            amount: Order amount
            stop_price: Stop trigger price
            params: Additional parameters

        Returns:
            Order response from exchange
        """
        try:
            formatted_stop = self.format_price(symbol, stop_price)
            formatted_amount = self.format_amount(symbol, amount)

            stop_params = params or {}
            stop_params['stopPrice'] = formatted_stop
            stop_params['type'] = 'STOP_MARKET'

            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'market',
                side,
                formatted_amount,
                None,
                stop_params
            )

            logger.info(
                f"Created stop-loss order: {formatted_amount} {symbol} @ {formatted_stop}"
            )
            return order

        except Exception as e:
            logger.error(f"Failed to create stop-loss order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Cancel an order"""
        try:
            result = await asyncio.to_thread(
                self.exchange.cancel_order,
                order_id,
                symbol
            )
            logger.info(f"Cancelled order {order_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    async def get_order(self, order_id: str, symbol: str) -> Dict:
        """Get order details"""
        try:
            return await asyncio.to_thread(
                self.exchange.fetch_order,
                order_id,
                symbol
            )
        except Exception as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
            raise

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        try:
            return await asyncio.to_thread(
                self.exchange.fetch_open_orders,
                symbol
            )
        except Exception as e:
            logger.error(f"Failed to fetch open orders: {e}")
            raise

    async def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for symbol"""
        try:
            positions = await asyncio.to_thread(
                self.exchange.fetch_positions,
                [symbol]
            )

            for pos in positions:
                if pos['symbol'] == symbol and float(pos.get('contracts', 0)) > 0:
                    return pos

            return None

        except Exception as e:
            logger.error(f"Failed to fetch position: {e}")
            raise

    async def get_balance(self) -> Dict:
        """Get account balance"""
        try:
            return await asyncio.to_thread(self.exchange.fetch_balance)
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            raise

    async def close_position(self, symbol: str, amount: Optional[float] = None):
        """
        Close position (or partial position)

        Args:
            symbol: Trading symbol
            amount: Amount to close (None = close all)
        """
        try:
            position = await self.get_position(symbol)
            if not position:
                logger.warning(f"No position found for {symbol}")
                return

            contracts = float(position.get('contracts', 0))
            side = position.get('side')  # 'long' or 'short'

            if contracts == 0:
                logger.warning(f"Position size is 0 for {symbol}")
                return

            close_amount = amount if amount else contracts
            close_side = 'sell' if side == 'long' else 'buy'

            # Close with market order
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'market',
                close_side,
                close_amount,
                None,
                {'reduceOnly': True}
            )

            logger.info(f"Closed position: {close_amount} {symbol}")
            return order

        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            raise

    def calculate_position_size(
        self,
        symbol: str,
        usd_size: float,
        price: float,
        leverage: int
    ) -> float:
        """
        Calculate position size in contracts from USD value

        Args:
            symbol: Trading symbol
            usd_size: Size in USD
            price: Entry price
            leverage: Leverage multiplier

        Returns:
            Position size in contracts
        """
        # For perpetual swaps, contract size is typically in base currency
        # Position in base currency = USD size / price
        contracts = usd_size / price
        return self.format_amount(symbol, contracts)
