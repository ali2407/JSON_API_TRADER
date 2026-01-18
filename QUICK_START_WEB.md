# Quick Start - Web Dashboard

## What You Have Now

A modern web-based trading terminal with:
- **Backend API**: FastAPI + SQLite + WebSockets
- **Frontend**: Next.js + React + Tailwind CSS
- **Dashboard**: Trade overview and statistics
- **Trades Page**: View and manage all your positions

## Currently Running

✅ **Backend API**: http://localhost:8000
✅ **Frontend**: http://localhost:3000
✅ **API Docs**: http://localhost:8000/docs

## Access Your Dashboard

Open your browser and go to:
```
http://localhost:3000
```

You'll see:
- **Dashboard** (`/dashboard`) - Overview of all trades and statistics
- **Trades** (`/trades`) - Detailed view of all positions with filters
- **Chart** (`/chart`) - Coming soon
- **Accounts** (`/accounts`) - Coming soon

## How to Use

### 1. View Dashboard
The dashboard shows:
- Total trades count
- Connected accounts
- Unrealized & Realized P&L
- Trade status breakdown (Pending/Active/Open/Closed)

### 2. View Trades
Click "Trades" in the sidebar to see:
- All your trade positions as cards
- Filter by status: All, Pending, Active, Open, Closed
- Each card shows: Symbol, Direction, Status, Margin, Leverage, Entry, Stop Loss
- Live position data for active trades

### 3. Create a Test Trade (via API)

```bash
curl -X POST http://localhost:8000/api/trades/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "SOL",
    "direction": "SHORT",
    "margin_usd": 1000,
    "leverage": "4x",
    "entry_price": 200.405,
    "stop_loss": 225.355,
    "entries": [
      {
        "label": "Entry",
        "price": 200.405,
        "size_usd": 66.67,
        "average_after_fill": 200.405
      }
    ],
    "take_profits": [
      {
        "level": "TP1",
        "price": 198.455,
        "size_percent": 25
      },
      {
        "level": "TP2",
        "price": 196.649,
        "size_percent": 25
      }
    ]
  }'
```

Then refresh your browser - the trade will appear!

## Next Steps

### Import from JSON
You can modify the backend to import your existing JSON trade plans:

1. Add a file upload endpoint in `backend/routers/trades.py`
2. Use `TradeLoader` from `src/trade_loader.py` to parse JSON
3. Convert to database format and save

### Connect to BingX
To actually execute trades:

1. The `start_trade` endpoint in `backend/routers/trades.py` needs to:
   - Initialize BingX client (from `src/bingx_client.py`)
   - Place orders on the exchange
   - Start position monitoring
   - Broadcast updates via WebSocket

2. Add a monitoring loop that:
   - Checks for fills
   - Updates position data
   - Broadcasts to frontend via WebSocket

### Real-time Updates
Frontend already has WebSocket client (`lib/useWebSocket.ts`). Backend just needs to broadcast trade updates when they change.

## Stopping Services

To stop both services:
```bash
# Find the processes
ps aux | grep uvicorn
ps aux | grep next

# Kill them
kill <PID>
```

Or use the shell IDs:
- Backend: f3a772
- Frontend: 30a2f9

## Troubleshooting

### Can't access http://localhost:3000
- Check frontend is running: `ps aux | grep next`
- Check for errors in terminal output

### API not working
- Check backend is running: `curl http://localhost:8000/health`
- Check API docs: http://localhost:8000/docs

### Database issues
- Delete and recreate: `rm data/trading_terminal.db`
- Backend will auto-create on restart

## File Structure

```
JSON_API_TRADER/
├── backend/              # FastAPI backend
│   ├── main.py          # API server
│   ├── database.py      # SQLite setup
│   ├── models.py        # Database models
│   ├── schemas.py       # API schemas
│   ├── crud.py          # Database operations
│   └── routers/
│       └── trades.py    # Trade endpoints
├── frontend/            # Next.js frontend
│   ├── app/            # Pages (dashboard, trades)
│   ├── components/     # TradeCard, Sidebar
│   ├── lib/            # API client, WebSocket
│   └── types/          # TypeScript types
├── data/               # SQLite database
└── WEB_DASHBOARD_README.md  # Full documentation
```

---

**Enjoy your new web dashboard!** 🚀
