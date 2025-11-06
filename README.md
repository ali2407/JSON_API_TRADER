# JSON API Trader

Automated trading terminal for executing and managing trades via BingX API using JSON trade plans.

## Features

- **JSON Trade Plans**: Import structured trade setups with entries, rebuys, and take-profit levels
- **Automated Execution**: Places all entry/rebuy orders and manages position automatically
- **Dynamic Stop Loss**: Adjusts SL as rebuys fill and moves SL to profit when TP1 hits
- **TP Cascade**: Each TP level becomes the next SL level, locking in profits progressively
- **Real-time Monitoring**: Continuously watches position and adjusts orders
- **Terminal UI**: Clean, interactive terminal interface with live trade status

## Strategy Logic

### Entry Management
1. Places all entry and rebuy limit orders at initialization
2. As each order fills, updates SL to cover entire accumulated position
3. After first entry fills, places all TP orders

### Take Profit & Stop Loss Logic
- **TP1 hits**: Close X% of position, move SL just above entry price (risk-free)
- **TP2 hits**: Close Y% of position, move SL just above TP1 price
- **TP3+ hits**: Continue cascade - each TP becomes next SL level
- **SL always closes entire remaining position**

### Example Flow (SHORT trade)
```
Entry @ 0.0222 → SL @ 0.024699
RB1 @ 0.023 fills → Update SL to cover full position
RB2 @ 0.0238 fills → Update SL to cover full position
TP1 @ 0.0219 hits → Close 20%, move SL to ~0.0222 (above entry) ✓ RISK-FREE
TP2 @ 0.0218 hits → Close 20%, move SL to ~0.0219 (above TP1)
TP3 @ 0.0217 hits → Close 20%, move SL to ~0.0218 (above TP2)
```

## Installation

### Prerequisites
- Python 3.8+
- BingX account with API access
- BingX API key and secret

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Edit `.env` and add your BingX credentials:
```env
BINGX_API_KEY=your_api_key_here
BINGX_API_SECRET=your_api_secret_here
DEFAULT_LEVERAGE=5
TESTNET=true  # Set to false for live trading
```

## Usage

### 1. Start the Terminal
```bash
python main.py
```

### 2. Load a Trade Plan

In the terminal UI:
- Enter the path to your JSON trade file in the input field
- Click "Load Trade" or press `l`
- The trade plan will be validated and displayed

You can use relative paths (from `trades/` directory) or absolute paths:
```
example_trade.json
trades/my_trade.json
/full/path/to/trade.json
```

### 3. Start Trade Execution

- Click "Start Trade" or press `s`
- The system will:
  - Set leverage
  - Place all entry/rebuy limit orders
  - Begin monitoring position
  - Automatically manage SL/TP adjustments

### 4. Monitor Trade

The UI displays:
- **Trade Status**: Current position, fills, SL level, profit status
- **Order Book**: All entry/rebuy orders and their status
- **Activity Log**: Real-time events and actions

### 5. Manual Controls

- **Cancel All** (`c`): Cancel all open orders
- **Close Position**: Immediately close entire position
- **Quit** (`q`): Exit terminal (does NOT close positions)

## Trade Plan JSON Format

```json
{
  "tradeSetup": {
    "symbol": "VET",              // Trading symbol
    "direction": "LONG|SHORT",     // Trade direction
    "dateTime": "2025-11-06 11:41:34",
    "marginUSD": 1000,             // Total margin allocation
    "entryPrice": 0.022153,        // Initial entry price
    "averagePrice": 0.02362,       // Expected average after all rebuys
    "stopLoss": 0.024699,          // Initial stop loss price
    "leverage": "5x",              // Leverage to use
    "maxLossPercent": 25           // Max loss percentage
  },
  "orderEntries": [                // Entry + Rebuy levels
    {
      "label": "Entry",
      "sizeUSD": 66.67,            // Size in USD for this level
      "price": 0.0222,             // Limit order price
      "average": 0.0222            // Average price after this fill
    },
    {
      "label": "RB1",
      "sizeUSD": 133.33,
      "price": 0.023,
      "average": 0.0227
    }
  ],
  "takeProfits": [                 // Take profit levels
    {
      "level": "TP1",
      "price": 0.0219,             // TP price
      "sizePercent": 20            // % of position to close (0-100)
    },
    {
      "level": "TP2",
      "price": 0.0218,
      "sizePercent": 20
    }
  ],
  "notes": "Optional notes about the trade"
}
```

### Validation Rules

- **LONG trades**: Stop loss < entry price, TPs > entry price
- **SHORT trades**: Stop loss > entry price, TPs < entry price
- Total entry sizes must equal `marginUSD`
- Total TP percentages must not exceed 100%

## Configuration

Edit `src/config.py` or `.env` for:

- `SL_OFFSET_PERCENT`: Gap between TP and new SL (default: 0.1%)
- `DEFAULT_LEVERAGE`: Default leverage if not in trade plan
- `TESTNET`: Use BingX testnet (true/false)

## Logging

All activity is logged to:
- **Terminal UI**: Activity log panel
- **File**: `logs/trader.log`

Log includes:
- Order placements and fills
- SL/TP adjustments
- Position updates
- Errors and warnings

## Safety Features

- Validates all trade plans before execution
- Uses `reduceOnly` flag for TP orders
- Monitors position continuously
- Automatic SL adjustment prevents over-exposure
- Testnet mode for safe testing

## Important Notes

### Risk Management
- Always test in TESTNET mode first
- Double-check trade plans before execution
- Monitor positions actively
- Never risk more than you can afford to lose

### API Limitations
- Respect BingX rate limits (handled by CCXT)
- Ensure API keys have futures trading permissions
- Check minimum order sizes for your symbols

### Network Connectivity
- Requires stable internet connection
- Position monitoring runs continuously
- Disconnect may miss fills - system will resync on next check

## Troubleshooting

### "API credentials not configured"
- Check `.env` file exists and has correct credentials
- Ensure no extra spaces in API key/secret

### "Market not found"
- Verify symbol format (e.g., VET, not VET/USDT)
- Check symbol is available on BingX perpetual futures

### Orders not filling
- Check price levels are realistic
- Verify leverage is set correctly
- Ensure sufficient margin in account

### Position not updating
- Check internet connection
- Look for errors in `logs/trader.log`
- Verify API permissions

## Development

### Project Structure
```
JSON_API_TRADER/
├── src/
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   ├── trade_loader.py    # JSON loader
│   ├── bingx_client.py    # API client
│   ├── order_manager.py   # Order execution
│   ├── strategy.py        # Trading logic
│   └── ui.py             # Terminal UI
├── trades/                # Trade plan JSONs
├── logs/                  # Log files
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── .env                  # Configuration (create from .env.example)
```

### Adding Features
- Extend `TradingStrategy` for new logic
- Modify `TradePlan` model for additional fields
- Update UI in `TradingTerminalApp`

## License

MIT License - Use at your own risk

## Disclaimer

This software is for educational purposes. Trading cryptocurrencies carries substantial risk. The authors are not responsible for any financial losses incurred through the use of this software.

Always:
- Test thoroughly in testnet mode
- Understand the strategy before using
- Monitor positions actively
- Use appropriate position sizing
- Never trade with money you can't afford to lose
