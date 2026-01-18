"""BTCC API client wrapper - Updated for correct BTCC API"""
import asyncio
import aiohttp
import hashlib
import time
import logging
from typing import Dict, List, Optional, Literal
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class BTCCClient:
    """Wrapper for BTCC exchange API"""

    # BTCC API base URL (from official documentation)
    BASE_URL = "https://api1.btloginc.com:9081"

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize BTCC client

        Args:
            api_key: BTCC API key
            api_secret: BTCC API secret (used for signing)
            testnet: Not supported by BTCC
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session: Optional[aiohttp.ClientSession] = None

        # Authentication state
        self.token: Optional[str] = None
        self.account_id: Optional[int] = None
        self.user_id: Optional[int] = None

        # Market data
        self.markets = {}
        self.precision_cache = {}
        self.symbol_map = {}  # Maps simple symbols like "BTCUSDT" to full BTCC names

    def _sign(self, params: Dict) -> str:
        """
        Generate MD5 signature for BTCC API

        Args:
            params: Request parameters including secret_key

        Returns:
            MD5 hash signature
        """
        # Sort parameters alphabetically
        sorted_params = {k: params[k] for k in sorted(params.keys())}
        query_string = urlencode(sorted_params)

        # MD5 hash
        signature = hashlib.md5(query_string.encode('utf-8')).hexdigest()
        return signature

    def _build_signed_params(self, params: Dict) -> Dict:
        """Build parameters with signature for authenticated requests"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        signed_params = {
            **params,
            'token': self.token,
            'secret_key': self.api_secret,
        }

        # Generate signature
        sign = self._sign(signed_params)

        # Remove secret_key from final params (only used for signing)
        del signed_params['secret_key']
        signed_params['sign'] = sign

        return signed_params

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = True
    ) -> Dict:
        """
        Make API request

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether to sign the request

        Returns:
            API response as dict
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"

        request_params = params or {}

        if signed:
            request_params = self._build_signed_params(request_params)

        try:
            logger.debug(f"BTCC API {method} {endpoint}: {request_params}")

            if method.upper() == 'GET':
                async with session.get(url, params=request_params) as response:
                    data = await response.json()
            else:
                async with session.post(url, data=request_params) as response:
                    data = await response.json()

            logger.debug(f"BTCC API response: {data}")

            # Check for errors
            if data.get('code', 0) != 0:
                error_msg = data.get('msg', 'Unknown error')
                raise Exception(f"BTCC API Error: {error_msg} (code: {data.get('code')})")

            return data

        except aiohttp.ClientError as e:
            logger.error(f"BTCC API request failed: {e}")
            raise

    async def login(self, user_name: str, password: str, company_id: int = 1) -> bool:
        """
        Login to BTCC API to get authentication token

        Args:
            user_name: Email or phone number
            password: Account password
            company_id: Company ID (default: 1)

        Returns:
            True if login successful
        """
        params = {
            'user_name': user_name,
            'password': password,
            'company_id': company_id,
            'api_key': self.api_key,
            'secret_key': self.api_secret,
        }

        # Generate signature
        sign = self._sign(params)
        del params['secret_key']
        params['sign'] = sign

        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/v1/user/login"

            logger.info(f"BTCC Login attempt: user={user_name}, company_id={company_id}, api_key={self.api_key[:8]}...")
            logger.debug(f"BTCC Login params (excluding sign): user_name={user_name}, company_id={company_id}")

            async with session.post(url, data=params) as response:
                data = await response.json()
                logger.info(f"BTCC Login response: code={data.get('code')}, msg={data.get('msg')}")
                logger.debug(f"BTCC Login full response: {data}")

            if data.get('code', -1) != 0:
                error_msg = data.get('msg', 'Unknown error')
                error_code = data.get('code', -1)
                # Provide more helpful error messages
                if error_msg == "API KEY NOT TRADE AUTH":
                    logger.error(
                        f"BTCC API Key lacks trading authorization. "
                        f"This API is for BTCC 'Futures' product (not 'Futures Pro'). "
                        f"Please create an API key with 'Futures - Read' and 'Futures - Trade' permissions, "
                        f"not 'Futures Pro' permissions."
                    )
                raise Exception(f"BTCC Login failed: {error_msg} (code: {error_code})")

            self.token = data.get('token')
            account = data.get('account', {})
            self.account_id = account.get('id')
            self.user_id = account.get('userid')

            logger.info(f"BTCC Login successful. Account ID: {self.account_id}, User ID: {self.user_id}")
            return True

        except Exception as e:
            logger.error(f"BTCC Login failed: {e}")
            raise

    async def initialize(self):
        """Load markets and initialize client"""
        if not self.token:
            logger.warning("Not logged in. Markets will not be loaded.")
            return

        try:
            # Get available symbols/products
            params = self._build_signed_params({
                'accountid': self.account_id,
            })

            session = await self._get_session()
            url = f"{self.BASE_URL}/v1/config/symbollist"

            async with session.get(url, params=params) as response:
                data = await response.json()

            if data.get('code', -1) != 0:
                raise Exception(f"Failed to get symbols: {data.get('msg')}")

            symbols = data.get('symbols', [])

            for symbol_info in symbols:
                full_name = symbol_info.get('name', '')
                base_currency = symbol_info.get('base_currency', '')
                profit_currency = symbol_info.get('profit_currency', '')

                # Create simple symbol mapping (e.g., "BTCUSDT" -> full BTCC name)
                simple_symbol = f"{base_currency}{profit_currency}"

                self.markets[full_name] = symbol_info
                self.symbol_map[simple_symbol] = full_name

                self.precision_cache[full_name] = {
                    'price': symbol_info.get('digits', 2),
                    'amount': 4,  # Default, adjust based on volumes_step
                    'min_volume': symbol_info.get('volumes_min', 0.01),
                    'max_volume': symbol_info.get('volumes_max', 10),
                    'volume_step': symbol_info.get('volumes_step', 0.01),
                }

            logger.info(f"Loaded {len(self.markets)} markets from BTCC")

        except Exception as e:
            logger.warning(f"Failed to load BTCC markets: {e}")

    async def keepalive(self):
        """Send heartbeat to maintain connection"""
        if not self.token:
            return

        try:
            params = self._build_signed_params({
                'accountid': self.account_id,
            })

            session = await self._get_session()
            url = f"{self.BASE_URL}/v1/user/keepalive"

            async with session.get(url, params=params) as response:
                data = await response.json()

            if data.get('code', -1) != 0:
                logger.warning(f"Heartbeat failed: {data.get('msg')}")

        except Exception as e:
            logger.warning(f"Heartbeat error: {e}")

    def get_full_symbol(self, simple_symbol: str) -> str:
        """
        Convert simple symbol (BTCUSDT) to full BTCC symbol name

        Args:
            simple_symbol: Simple symbol like "BTCUSDT" or "XRPUSDT"

        Returns:
            Full BTCC symbol name
        """
        # Clean the symbol
        clean_symbol = simple_symbol.replace("/", "").replace(":", "").upper()

        if clean_symbol in self.symbol_map:
            return self.symbol_map[clean_symbol]

        # If not found, return as-is (may fail on API call)
        logger.warning(f"Symbol {clean_symbol} not found in market map")
        return clean_symbol

    def get_precision(self, symbol: str) -> Dict:
        """Get price and amount precision for symbol"""
        if symbol in self.precision_cache:
            return self.precision_cache[symbol]
        return {'price': 2, 'amount': 4, 'min_volume': 0.01, 'max_volume': 10, 'volume_step': 0.01}

    def format_price(self, symbol: str, price: float) -> float:
        """Format price according to symbol precision"""
        precision = self.get_precision(symbol)
        price_precision = precision.get('price', 2)
        return float(Decimal(str(price)).quantize(
            Decimal(str(10 ** -price_precision)),
            rounding=ROUND_DOWN
        ))

    def format_amount(self, symbol: str, amount: float) -> float:
        """Format amount according to symbol precision"""
        precision = self.get_precision(symbol)
        volume_step = precision.get('volume_step', 0.01)

        # Round to volume step
        if volume_step > 0:
            amount = float(Decimal(str(amount)) // Decimal(str(volume_step)) * Decimal(str(volume_step)))

        return max(amount, precision.get('min_volume', 0.01))

    async def set_leverage(self, symbol: str, leverage: int):
        """
        BTCC sets leverage per-position, not globally.
        This is handled in open_position.
        """
        logger.info(f"BTCC: Leverage {leverage}x will be set when opening position for {symbol}")
        return {'success': True, 'leverage': leverage}

    async def open_position(
        self,
        symbol: str,
        direction: Literal["buy", "sell"],
        volume: float,
        price: float,
        leverage: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Dict:
        """
        Open a position on BTCC

        Args:
            symbol: Full BTCC symbol name
            direction: 'buy' (long) or 'sell' (short)
            volume: Position size
            price: Entry price
            leverage: Leverage multiplier
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price

        Returns:
            Position response from exchange
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        # Map direction to BTCC format (1=Buy, 2=Sell)
        direction_code = 1 if direction.lower() == 'buy' else 2

        params = {
            'accountid': self.account_id,
            'direction': direction_code,
            'symbol': symbol,
            'request_volume': self.format_amount(symbol, volume),
            'request_price': self.format_price(symbol, price),
            'multiple': leverage,
        }

        if stop_loss and stop_loss > 0:
            params['stop_loss'] = self.format_price(symbol, stop_loss)
        if take_profit and take_profit > 0:
            params['take_profit'] = self.format_price(symbol, take_profit)

        try:
            result = await self._request('POST', '/v1/account/openposition', params)

            position = result.get('position', {})
            logger.info(
                f"BTCC: Opened {direction} position: {volume} {symbol} @ {price} "
                f"(ID: {position.get('id')})"
            )

            return {
                'id': str(position.get('id', '')),
                'symbol': symbol,
                'side': direction,
                'amount': volume,
                'price': price,
                'status': 'open' if position.get('status') == 1 else 'pending',
                'raw': result,
            }

        except Exception as e:
            logger.error(f"Failed to open position: {e}")
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
        Create a limit order (pending order) on BTCC

        Note: BTCC uses "pending orders" for limit orders
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        # Get leverage from params or default to 1
        leverage = params.get('leverage', 1) if params else 1

        # Map to BTCC direction (1=Buy, 2=Sell)
        direction_code = 1 if side.lower() == 'buy' else 2

        # Type 1 = LIMIT open order
        order_params = {
            'accountid': self.account_id,
            'direction': direction_code,
            'type': 1,  # LIMIT open
            'symbol': symbol,
            'request_volume': self.format_amount(symbol, amount),
            'request_price': self.format_price(symbol, price),
            'multiple': leverage,
        }

        if params:
            if 'stop_loss' in params:
                order_params['stop_loss'] = self.format_price(symbol, params['stop_loss'])
            if 'take_profit' in params:
                order_params['take_profit'] = self.format_price(symbol, params['take_profit'])

        try:
            result = await self._request('POST', '/v1/account/openpending', order_params)

            order = result.get('order', {})
            logger.info(
                f"BTCC: Created {side} limit order: {amount} {symbol} @ {price} "
                f"(ID: {order.get('id')})"
            )

            return {
                'id': str(order.get('id', '')),
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'type': 'limit',
                'status': 'open',
                'raw': result,
            }

        except Exception as e:
            logger.error(f"Failed to create limit order: {e}")
            raise

    async def create_market_order(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        amount: float,
        params: Optional[Dict] = None
    ) -> Dict:
        """Create a market order (opens position immediately)"""
        leverage = params.get('leverage', 1) if params else 1

        # For market orders, use current price (0 or fetch from market)
        # BTCC's openposition with request_price=0 should work as market
        return await self.open_position(
            symbol=symbol,
            direction=side,
            volume=amount,
            price=0,  # Market price
            leverage=leverage,
            stop_loss=params.get('stop_loss') if params else None,
            take_profit=params.get('take_profit') if params else None,
        )

    async def create_stop_loss_order(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        amount: float,
        stop_price: float,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Create a stop-loss order on BTCC

        Note: BTCC handles SL/TP as order modifications or separate orders
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        position_id = params.get('positionid') if params else None
        leverage = params.get('leverage', 1) if params else 1

        if position_id:
            # Create SL for existing position using opensltp
            order_params = {
                'accountid': self.account_id,
                'symbol': symbol,
                'request_volume': self.format_amount(symbol, amount),
                'stop_loss': self.format_price(symbol, stop_price),
                'multiple': leverage,
                'positionid': position_id,
            }

            result = await self._request('POST', '/v1/account/opensltp', order_params)
        else:
            # Create as stop order (type=2)
            direction_code = 1 if side.lower() == 'buy' else 2

            order_params = {
                'accountid': self.account_id,
                'direction': direction_code,
                'type': 2,  # STOP open
                'symbol': symbol,
                'request_volume': self.format_amount(symbol, amount),
                'request_price': self.format_price(symbol, stop_price),
                'multiple': leverage,
            }

            result = await self._request('POST', '/v1/account/openpending', order_params)

        order = result.get('order', {})
        logger.info(f"BTCC: Created stop-loss order @ {stop_price} (ID: {order.get('id')})")

        return {
            'id': str(order.get('id', '')),
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'stopPrice': stop_price,
            'type': 'stop_loss',
            'status': 'open',
            'raw': result,
        }

    async def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Cancel a pending order"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        params = {
            'accountid': self.account_id,
            'id': int(order_id),
        }

        result = await self._request('POST', '/v1/account/cancelpending', params)
        logger.info(f"BTCC: Cancelled order {order_id}")
        return result

    async def get_order(self, order_id: str, symbol: str) -> Dict:
        """Get order details - fetch from order list"""
        orders = await self.get_open_orders(symbol)
        for order in orders:
            if str(order.get('id')) == str(order_id):
                return order
        return {}

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open/pending orders"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        params = {
            'accountid': self.account_id,
        }

        if symbol:
            params['symbol'] = symbol

        result = await self._request('GET', '/v1/account/orderList', params)
        return result.get('orders', [])

    async def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for symbol"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        params = {
            'accountid': self.account_id,
            'symbol': symbol,
            'pageNo': 1,
            'pageSize': 100,
        }

        result = await self._request('GET', '/v1/account/positionlist', params)
        positions = result.get('positions', [])

        for pos in positions:
            if pos.get('symbol') == symbol and pos.get('status') == 1:
                return {
                    'id': pos.get('id'),
                    'symbol': symbol,
                    'side': 'long' if pos.get('direction') == 1 else 'short',
                    'contracts': pos.get('volume', 0),
                    'entryPrice': pos.get('open_price', 0),
                    'unrealizedPnl': pos.get('profit', 0),
                    'raw': pos,
                }

        return None

    async def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        params = {
            'accountid': self.account_id,
            'pageNo': 1,
            'pageSize': 100,
        }

        result = await self._request('GET', '/v1/account/positionlist', params)
        positions = result.get('positions', [])

        return [
            {
                'id': pos.get('id'),
                'symbol': pos.get('symbol'),
                'side': 'long' if pos.get('direction') == 1 else 'short',
                'contracts': pos.get('volume', 0),
                'entryPrice': pos.get('open_price', 0),
                'unrealizedPnl': pos.get('profit', 0),
                'raw': pos,
            }
            for pos in positions
            if pos.get('status') == 1
        ]

    async def get_balance(self) -> Dict:
        """Get account balance"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        params = {
            'accountid': self.account_id,
        }

        result = await self._request('GET', '/v1/account/account', params)
        account = result.get('account', {})

        return {
            'balance': account.get('balance', 0),
            'equity': account.get('equity', 0),
            'margin': account.get('margin', 0),
            'freeMargin': account.get('free_margin', 0),
            'marginLevel': account.get('margin_level', 0),
            'raw': account,
        }

    async def close_position(self, symbol: str, amount: Optional[float] = None):
        """
        Close position (or partial position)

        Args:
            symbol: Trading symbol
            amount: Amount to close (None = close all)
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        position = await self.get_position(symbol)
        if not position:
            logger.warning(f"No position found for {symbol}")
            return None

        position_id = position['id']
        contracts = position['contracts']
        side = position['side']

        if contracts == 0:
            logger.warning(f"Position size is 0 for {symbol}")
            return None

        close_amount = amount if amount else contracts
        # Close direction is opposite of position
        close_direction = 2 if side == 'long' else 1  # 2=Sell to close long, 1=Buy to close short

        params = {
            'accountid': self.account_id,
            'positionid': position_id,
            'direction': close_direction,
            'symbol': symbol,
            'request_volume': self.format_amount(symbol, close_amount),
            'request_price': 0,  # Market price
        }

        result = await self._request('POST', '/v1/account/closeposition', params)
        logger.info(f"BTCC: Closed position {close_amount} {symbol}")
        return result

    def calculate_position_size(
        self,
        symbol: str,
        usd_size: float,
        price: float,
        leverage: int
    ) -> float:
        """
        Calculate position size from USD value

        Args:
            symbol: Trading symbol
            usd_size: Size in USD
            price: Entry price
            leverage: Leverage multiplier

        Returns:
            Position size
        """
        contracts = usd_size / price
        return self.format_amount(symbol, contracts)

    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
