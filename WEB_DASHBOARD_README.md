# Web Dashboard for Trading Terminal

This is a modern web-based dashboard for managing your automated trading positions.

## Stack

- **Backend**: FastAPI + SQLite + WebSockets
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS + TypeScript

## Project Structure

```
JSON_API_TRADER/
├── backend/              # FastAPI backend
│   ├── main.py          # Main FastAPI app
│   ├── database.py      # Database setup
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── routers/         # API route handlers
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   ├── lib/            # Utilities & API client
│   └── types/          # TypeScript types
└── data/               # SQLite database (auto-created)
```

## Quick Start

### 1. Backend Setup

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws

### 2. Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Create .env file
cp .env.example .env

# Run frontend dev server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Features

### Dashboard Page
- Trade overview statistics
- Total trades count (Pending, Active, Open, Closed)
- Unrealized & Realized P&L
- Quick actions (Import Trade, Connect Account)

### Trades Page
- View all trades with status filtering
- Trade cards showing:
  - Symbol, Direction (LONG/SHORT), Status
  - Margin, Leverage, Entry, Stop Loss
  - Live position data (size, mark price, P&L)
  - Take Profit levels and fill status
  - Entry/Rebuy orders and fill status
- Actions: Edit, Close position
- Real-time refresh via WebSocket

### Trade Card Components
- Color-coded status badges
- Direction indicators (🔼 LONG / 🔽 SHORT)
- Filled/Pending order status
- Live position monitoring
- P&L tracking

## API Endpoints

### Trades
- `GET /api/trades` - Get all trades (optional ?status filter)
- `GET /api/trades/{id}` - Get specific trade
- `POST /api/trades` - Create new trade
- `PATCH /api/trades/{id}` - Update trade
- `DELETE /api/trades/{id}` - Delete trade
- `POST /api/trades/{id}/start` - Start trade execution
- `POST /api/trades/{id}/close` - Close trade position
- `GET /api/trades/summary` - Get dashboard statistics

### WebSocket
- `WS /ws` - Real-time trade updates

## Database Schema

### Trade
- Trade setup (symbol, direction, margin, leverage)
- Position state (size, avg entry, SL, P&L)
- Status tracking (pending → active → open → closed)
- Timestamps

### OrderEntry
- Entry and rebuy orders
- Price, size, fill status
- Linked to trade

### TakeProfit
- TP levels with prices and percentages
- Fill status tracking
- Linked to trade

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python -m uvicorn main:app --reload

# Check database
sqlite3 ../data/trading_terminal.db
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

## Next Steps (TODO)

1. **Import Trade from JSON**
   - Add file upload functionality
   - Parse existing JSON trade plans
   - Convert to database format

2. **Integration with BingX Client**
   - Connect backend to existing `src/bingx_client.py`
   - Real order placement when "Start Trade" is clicked
   - Live position updates from exchange
   - WebSocket broadcast on fills/updates

3. **Real-time Updates**
   - Backend monitoring loop
   - WebSocket broadcasts to all connected clients
   - Auto-refresh trades on frontend

4. **Account Management**
   - Add multiple API keys
   - Switch between accounts
   - Display account balance

5. **Advanced Features**
   - Edit trade plans
   - Manual TP adjustment
   - Trade history & analytics
   - Export trade reports

## Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Ensure all dependencies installed: `pip install -r backend/requirements.txt`

### Frontend won't start
- Check Node version (18+)
- Clear cache: `rm -rf frontend/.next frontend/node_modules`
- Reinstall: `npm install`

### Database errors
- Delete and recreate: `rm data/trading_terminal.db`
- Backend will auto-create on next startup

### CORS errors
- Ensure backend CORS allows `http://localhost:3000`
- Check frontend `.env` has correct API URL

## Screenshots

The dashboard provides:
- Clean, modern dark theme UI
- Real-time position monitoring
- Status-based filtering
- Mobile-responsive design
- Live WebSocket updates

---

**Built with FastAPI, Next.js, and modern web technologies** 🚀
