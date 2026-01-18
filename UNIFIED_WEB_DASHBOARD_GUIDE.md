# Unified Web Dashboard - Complete Guide

## 🎉 Everything in ONE Place!

Your trading terminal is now a **unified web dashboard** where you can:
- ✅ Add BingX API keys
- ✅ Import JSON trade files
- ✅ Start trades on BingX
- ✅ Monitor positions in real-time
- ✅ Close trades

**No more switching between terminal and web!** Everything happens at: **http://localhost:3000**

---

## 📍 Where Everything Is Stored

### SQLite Database Location
```
/Users/albert/JSON_API_TRADER/data/trading_terminal.db
```

This ONE file contains ALL your data:
- API keys (encrypted)
- Trades
- Orders
- Take profits
- Position history

**Backup this file** to backup everything!

---

## 🚀 How to Use (Step-by-Step)

### Step 1: Add Your BingX API Key

1. Go to: **http://localhost:3000/accounts**
2. Click **"Add API Key"** (green button)
3. Fill in the form:
   - **Name**: "My BingX Account"
   - **API Key**: [paste your BingX API key]
   - **API Secret**: [paste your secret]
   - **Use Testnet**: ✅ (recommended for testing!)
   - **Set as Default**: ✅
4. Click **"Add API Key"**

✅ Your API key is now stored and ready to use!

### Step 2: Import a Trade

1. Go to: **http://localhost:3000/dashboard**
2. Click **"Import Trade"** button
3. Select your JSON trade file (from `trades/` folder)
4. Click **"Import Trade"**

✅ Your trade is now in the system!

### Step 3: View Your Trade

1. Go to: **http://localhost:3000/trades**
2. You'll see your trade card with all details:
   - Symbol, Direction, Status
   - Margin, Leverage, Entry, Stop Loss
   - All take profit levels
   - All entry/rebuy orders

### Step 4: Start Trading on BingX!

1. On the trade card, click **"Start Trade"** button
2. Confirm the action
3. **What happens:**
   - System uses your stored API key
   - Connects to BingX
   - Sets leverage
   - Places all entry/rebuy limit orders
   - Activates stop loss
   - Starts monitoring position

✅ Your trade is now LIVE on BingX!

### Step 5: Monitor in Real-Time

The dashboard automatically:
- Tracks order fills
- Updates position size
- Adjusts stop loss as rebuys fill
- Monitors for take profit hits
- Shows current P&L

Click the refresh button 🔄 to get latest updates!

### Step 6: Close Trade

When you're done:
1. Click **"Close"** button on trade card
2. Confirm
3. System closes the entire position on BingX

---

## 📊 Dashboard Pages

### Dashboard (`/dashboard`)
- **Trade Statistics**: Total trades, pending, active, open, closed
- **P&L Summary**: Unrealized and realized profits
- **Quick Actions**:
  - Import Trade (JSON file upload)
  - Connect Account (add API keys)

### Trades (`/trades`)
- **Filter Tabs**: All, Pending, Active, Open, Closed
- **Trade Cards**: All your positions with full details
- **Actions**: Start, Close, Refresh each trade

### Accounts (`/accounts`)
- **API Keys List**: All your exchange accounts
- **Add New Key**: Connect more accounts
- **Manage Keys**: Set default, disable, delete

### Chart (`/chart`)
- Coming soon...

---

## 🔄 Trading Flow

```
1. Add API Key →
2. Import JSON Trade →
3. Trade appears as "PENDING" →
4. Click "Start Trade" →
5. Orders placed on BingX →
6. Status changes to "ACTIVE" →
7. Orders fill → Status becomes "OPEN" →
8. Monitor position →
9. Close trade → Status becomes "CLOSED"
```

---

## 🔐 Security

### API Keys
- Stored encrypted in database (base64 for now)
- Only show masked preview (first 4 + last 4 chars)
- Never displayed in full after saving
- Can be deleted anytime

### Database
- Local file on your computer
- Not accessible from internet
- Backup recommended

---

## 🛠️ Technical Details

### Backend (Python/FastAPI)
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws
- **Components**:
  - BingX Client (from `src/bingx_client.py`)
  - Order Manager (from `src/order_manager.py`)
  - Trading Strategy (from `src/strategy.py`)
  - Database (SQLite)
  - REST API endpoints
  - WebSocket for real-time updates

### Frontend (Next.js/React)
- **Dashboard**: http://localhost:3000
- **Components**:
  - Sidebar navigation
  - Trade cards
  - Import modal
  - API client
  - Real-time WebSocket connection

---

## 📝 Example JSON Trade Format

Place your JSON files in the `trades/` folder:

```json
{
  "tradeSetup": {
    "symbol": "SOL",
    "direction": "SHORT",
    "marginUSD": 1000,
    "entryPrice": 200.405,
    "averagePrice": 210.5,
    "stopLoss": 225.355,
    "leverage": "4x",
    "maxLossPercent": 25
  },
  "orderEntries": [
    {
      "label": "Entry",
      "sizeUSD": 200,
      "price": 200.405,
      "average": 200.405
    },
    {
      "label": "RB1",
      "sizeUSD": 300,
      "price": 210.0,
      "average": 206.0
    }
  ],
  "takeProfits": [
    {
      "level": "TP1",
      "price": 195.0,
      "sizePercent": 25
    },
    {
      "level": "TP2",
      "price": 190.0,
      "sizePercent": 25
    }
  ],
  "notes": "My SOL short trade"
}
```

---

## ⚠️ Important Notes

### Testing First!
1. **Always use TESTNET first!**
   - Check "Use Testnet" when adding API key
   - Test with small positions
   - Verify orders place correctly

2. **Live Trading**
   - Add new API key with testnet=false
   - Start with small positions
   - Monitor closely

### Order Execution
- Entry/rebuy orders placed as **limit orders**
- Take profits placed when first entry fills
- Stop loss updates automatically as rebuys fill
- All orders use `reduceOnly` flag where appropriate

### Position Monitoring
- Backend monitors position continuously
- Updates database in real-time
- WebSocket broadcasts changes to frontend
- Refresh button forces immediate update

### Error Handling
- If API key is invalid, trade won't start
- If no API key exists, you'll get an error
- All errors shown in UI alerts

---

## 🔧 Troubleshooting

### "No active API keys found"
→ Go to `/accounts` and add an API key

### Trade won't start
→ Check:
- API key is active (green badge)
- API key is valid
- Trade is in PENDING status

### Orders not appearing on BingX
→ Check:
- Using correct testnet/live setting
- API key has trading permissions
- Symbol exists on BingX

### Database issues
→ Delete and restart:
```bash
rm /Users/albert/JSON_API_TRADER/data/trading_terminal.db
# Restart backend - it will create new DB
```

### Backend not responding
→ Check if running:
```bash
curl http://localhost:8000/health
```

### Frontend not loading
→ Check if running:
```bash
ps aux | grep "next dev"
```

---

## 📦 Starting the System

### Option 1: Use the script
```bash
cd /Users/albert/JSON_API_TRADER
./run_web_dashboard.sh
```

### Option 2: Manual start

**Backend:**
```bash
cd /Users/albert/JSON_API_TRADER
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd /Users/albert/JSON_API_TRADER/frontend
npm run dev
```

Then open: **http://localhost:3000**

---

## 🎯 Quick Reference

| Action | Page | URL |
|--------|------|-----|
| Add API Key | Accounts | http://localhost:3000/accounts |
| Import Trade | Dashboard | http://localhost:3000/dashboard |
| View Trades | Trades | http://localhost:3000/trades |
| Start Trade | Trades | Click "Start Trade" on card |
| Close Trade | Trades | Click "Close" on card |
| API Docs | Backend | http://localhost:8000/docs |

---

**Everything is unified in ONE web dashboard!** 🚀

No more terminal app needed - just use the web interface!
