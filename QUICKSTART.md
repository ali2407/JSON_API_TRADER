# Quick Start Guide

Get up and running with JSON API Trader in 5 minutes.

## Step 1: Setup

Run the setup script:

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` file from template
- Create necessary directories

## Step 2: Configure API Credentials

Edit the `.env` file:

```bash
nano .env  # or use your preferred editor
```

Add your BingX API credentials:

```env
BINGX_API_KEY=your_actual_api_key
BINGX_API_SECRET=your_actual_api_secret
TESTNET=true  # Keep this true for testing!
```

### Getting BingX API Keys

1. Go to [BingX](https://bingx.com)
2. Login → Account → API Management
3. Create API Key with **Futures Trading** permissions
4. Copy API Key and Secret to `.env`

## Step 3: Run the Terminal

Activate virtual environment and start:

```bash
source venv/bin/activate
python main.py
```

## Step 4: Load a Trade

In the terminal UI:

1. Type `example_trade.json` in the input field
2. Click "Load Trade" (or press `l`)
3. Review the trade plan displayed

## Step 5: Start Trading

1. Click "Start Trade" (or press `s`)
2. Watch the terminal monitor your position automatically
3. The system will:
   - Place all entry/rebuy orders
   - Set stop loss
   - Monitor fills
   - Adjust SL/TP dynamically

## Trade Plan Example

The example trade (`trades/example_trade.json`) is a SHORT position on VET:

- **Entry**: 0.0222 ($66.67)
- **3 Rebuys**: 0.023, 0.0238, 0.0239
- **Stop Loss**: 0.024699
- **5 Take Profits**: 0.0219 → 0.0215 (20% each)

### What Happens:

1. System places 4 limit orders (Entry + 3 RBs)
2. When Entry fills → SL is activated
3. As rebuys fill → SL quantity increases
4. When TP1 hits → Close 20%, move SL above entry (risk-free!)
5. Each higher TP → Close more, move SL higher

## Creating Your Own Trade Plans

Copy the example and modify:

```bash
cp trades/example_trade.json trades/my_trade.json
nano trades/my_trade.json
```

### Key Points:

- **LONG**: SL below entry, TPs above
- **SHORT**: SL above entry, TPs below
- Total entry sizes = `marginUSD`
- TP percentages ≤ 100%

## Testing Strategy

### Phase 1: Testnet (REQUIRED)
```env
TESTNET=true
```

1. Test with small positions
2. Verify orders place correctly
3. Check SL/TP adjustments work
4. Monitor position tracking

### Phase 2: Live Trading (When Ready)
```env
TESTNET=false
```

1. Start with small positions
2. Monitor closely
3. Gradually increase size

## Common Commands

- `l` - Load trade
- `s` - Start trade
- `c` - Cancel all orders
- `q` - Quit (positions stay open!)

## Troubleshooting

### "API credentials not configured"
→ Check `.env` file has your actual API keys

### "Market not found"
→ Ensure symbol exists on BingX perpetual futures

### Orders not filling
→ Check prices are realistic for current market

### UI not updating
→ Check internet connection, see `logs/trader.log`

## Safety Checklist

Before each trade:

- [ ] Tested in TESTNET mode
- [ ] Reviewed trade plan JSON
- [ ] Checked position size is appropriate
- [ ] Verified stop loss is set correctly
- [ ] Confirmed TPs are in logical order
- [ ] Internet connection is stable

## Need Help?

- Read full documentation: `README.md`
- Check logs: `logs/trader.log`
- Review code: `src/` directory

## What's Next?

1. **Create trade plans**: Develop your own JSON files
2. **Backtest**: Analyze historical data for entry/SL/TP levels
3. **Optimize**: Adjust TP percentages and rebuy sizes
4. **Scale**: Gradually increase position sizes

---

**Remember**: This is real money. Test thoroughly, start small, and never risk more than you can afford to lose.

Happy trading! 🚀
