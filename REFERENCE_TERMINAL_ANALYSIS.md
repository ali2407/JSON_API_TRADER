# Reference Terminal Analysis: terminal.javlis.com

## Overview
Professional multi-exchange trading terminal. Version 2.12.6.

---

## 1. TECHNOLOGY STACK

### Frontend Framework
- **Framework**: Next.js (Turbopack bundler - modern build system)
- **React**: Server Components + Client Components
- **Styling**: Tailwind CSS with custom design system

### Fonts
- **Primary**: Outfit (variable font) - `outfit_3a2b1dcd-module__quYl0a__variable`
- **Monospace**: JetBrains Mono - `jetbrains_mono_5a51d796-module__23ALCq__variable`

### Charting Library
- **Library**: TradingView Lightweight Charts
- **Evidence**: `<div class="tv-lightweight-charts">` in DOM
- **Canvas Rendering**: Dual canvas layers (main chart + overlay)

### Icon Library
- **Lucide React** - All icons use `lucide lucide-*` classes

---

## 2. COLOR SCHEME & DESIGN SYSTEM

### Background Colors
| Element | Color | Hex |
|---------|-------|-----|
| Main background | Very dark blue | `#06080c` |
| Sidebar background | Dark blue | `#0a0d12` |
| Card/hover states | Dark gray | `#141922` |

### Border Colors
| Element | Color |
|---------|-------|
| Primary borders | `border-[#1e2530]` |
| Card borders | `border-gray-700/30` |

### Accent Colors
| Purpose | Color | Class |
|---------|-------|-------|
| Primary accent | Amber/Gold | `amber-500`, `amber-400` |
| Success/Positive | Emerald | `emerald-500`, `emerald-400` |
| Info/Active | Blue | `blue-500`, `blue-400` |
| Secondary | Violet | `violet-500`, `violet-400` |
| Danger/Short | Red | `red-500`, `red-400` |
| Neutral | Gray | `gray-400`, `gray-500`, `gray-600` |

### Status Badge Colors
```css
/* Pending */
bg-amber-500/10 border-amber-500/20 text-amber-400

/* Active */
bg-blue-500/10 border-blue-500/20 text-blue-400

/* Open/Success */
bg-emerald-500/10 border-emerald-500/20 text-emerald-400

/* Closed/Neutral */
bg-gray-500/5 border-gray-600/20 text-gray-400

/* Running status */
bg-emerald-500/10 border-emerald-500/30 text-emerald-400
```

---

## 3. LAYOUT STRUCTURE

### Main Container
```html
<div class="flex h-screen overflow-hidden bg-[#06080c]">
  <!-- Sidebar (hidden on mobile) -->
  <div class="hidden md:flex">
    <div class="w-56 bg-[#0a0d12] border-r border-[#1e2530] flex flex-col">
      <!-- Logo -->
      <!-- Navigation -->
      <!-- Version footer -->
    </div>
  </div>

  <!-- Main content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
    <header class="sticky top-0 z-30 h-12 bg-[#0a0d12] border-b border-[#1e2530]">
    </header>

    <!-- Content area -->
    <main class="flex-1 overflow-y-auto p-4 pb-20 md:p-6 md:pb-6 bg-[#06080c]">
    </main>
  </div>
</div>
```

### Sidebar Width
- Desktop: `w-56` (224px)
- Mobile: Hidden, hamburger menu

### Header Height
- `h-12` (48px) - slightly smaller than ours
- `h-14` (56px) for sidebar header

---

## 4. COMPONENT PATTERNS

### 4.1 Glass Card
```css
.glass-card {
  /* Likely defined in CSS, used throughout */
  /* Background with transparency and blur effect */
}
```
Usage: `<div class="glass-card rounded p-3 sm:p-5">`

### 4.2 Stat Cards
```html
<div class="glass-card rounded p-3 sm:p-5">
  <div class="flex items-start justify-between gap-2">
    <div class="min-w-0">
      <p class="text-[10px] sm:text-xs text-gray-500 font-medium uppercase tracking-wide">Label</p>
      <p class="text-xl sm:text-2xl font-semibold text-gray-100 mt-1 font-mono">Value</p>
      <div class="flex flex-wrap gap-x-2 gap-y-0.5 mt-1.5 sm:mt-2 text-[10px] sm:text-[11px]">
        <!-- Sub-stats -->
      </div>
    </div>
    <div class="p-2 sm:p-2.5 bg-amber-500/10 rounded flex-shrink-0">
      <!-- Icon -->
    </div>
  </div>
</div>
```

### 4.3 Navigation Item (Active)
```html
<a class="flex items-center gap-3 px-3 py-2.5 rounded transition-all text-sm font-medium
         bg-amber-500/10 border-l-2 border-amber-500 text-amber-400 ml-0"
   href="/dashboard">
  <svg class="lucide lucide-layout-dashboard w-4 h-4">...</svg>
  <span>Dashboard</span>
</a>
```

### 4.4 Navigation Item (Inactive)
```html
<a class="flex items-center gap-3 px-3 py-2.5 rounded transition-all text-sm font-medium
         text-gray-400 hover:bg-[#141922] hover:text-gray-200 border-l-2 border-transparent"
   href="/trades">
  <svg>...</svg>
  <span>Trades</span>
</a>
```

### 4.5 Status Badge (Live Indicator)
```html
<div class="flex items-center gap-2 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded">
  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
  <span class="text-[11px] font-medium text-emerald-400 uppercase tracking-wide">Live</span>
</div>
```

### 4.6 Direction Badge (LONG/SHORT)
```html
<!-- SHORT -->
<span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400">SHORT</span>

<!-- LONG (would be) -->
<span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400">LONG</span>
```

### 4.7 Action Buttons
```html
<!-- Primary action (amber) -->
<button class="flex items-center gap-1.5 px-3 py-2 bg-amber-500/10 hover:bg-amber-500/20
               border border-amber-500/30 text-amber-400 rounded text-sm font-medium transition-colors">
  <svg class="w-4 h-4">...</svg>
  Button Text
</button>

<!-- Danger action (red) -->
<button class="flex items-center gap-1.5 px-3 py-2 bg-red-500/10 hover:bg-red-500/20
               border border-red-500/30 text-red-400 rounded text-sm font-medium transition-colors">
  <svg class="w-4 h-4">...</svg>
  Stop
</button>
```

---

## 5. NAVIGATION STRUCTURE

### Routes
| Path | Label | Icon |
|------|-------|------|
| `/dashboard` | Dashboard | `layout-dashboard` |
| `/trades` | Trades | `trending-up` |
| `/chart` | Chart | `chart-column` |
| `/accounts` | Accounts | `wallet` |
| `/trades/new` | Import Trade | (quick action) |

### Trade Filters
- `/trades?filter=pending`
- `/trades?filter=active`
- `/trades?filter=open`
- `/trades?filter=closed`

---

## 6. DASHBOARD FEATURES

### 6.1 Stats Overview (4 cards)
1. **Trades** - Total count with breakdown (pending, active, open)
2. **Accounts** - Number of connected accounts
3. **Unrealized** - Unrealized PnL with position count
4. **Multi-Acc** - Multi-account trades

### 6.2 Auto-Placement Monitor
- Shows monitoring status (RUNNING/STOPPED)
- "Checks every 60s"
- "Last: Xs ago" timestamp
- Actions: Stop, Check Now

### 6.3 Trade Status Grid
- 4 clickable status cards
- Pending (amber)
- Active (blue)
- Open (emerald)
- Closed (gray)

### 6.4 Quick Actions
- Import Trade (amber) → `/trades/new`
- Add Account (emerald) → `/accounts`

### 6.5 Recent Activity Feed
Event types with icons:
- `TP/SL Set` - Shield icon (emerald)
- `Setting TP/SL` - Shield icon (amber)
- `Closed` - Circle check icon (emerald)
- `Closing` - Arrow right-left icon (amber)
- `Deployed` - Circle check icon (emerald)
- `Placing` - Clock icon (amber)

Activity item structure:
```html
<div class="bg-gray-800/30 border border-gray-700/30 rounded overflow-hidden">
  <div class="flex items-start gap-3 p-2.5 sm:p-3 cursor-pointer hover:bg-gray-800/50">
    <div class="p-1.5 rounded bg-gray-700/50"><!-- Icon --></div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-emerald-400">Event Type</span>
        <a class="text-xs font-mono text-gray-300 hover:text-amber-400">SYMBOL</a>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400">SHORT</span>
      </div>
      <div class="flex items-center gap-2 mt-1">
        <span class="text-[10px] text-gray-500">→ Account Name</span>
      </div>
    </div>
    <span class="text-[10px] text-gray-600">Date</span>
  </div>
</div>
```

---

## 7. TYPOGRAPHY SCALE

| Purpose | Size | Class |
|---------|------|-------|
| Page title | 24px | `text-xl sm:text-2xl` |
| Card title | 14px | `text-sm` |
| Card value | 24px | `text-xl sm:text-2xl font-mono` |
| Label | 10-12px | `text-[10px] sm:text-xs uppercase tracking-wide` |
| Body text | 11-12px | `text-[11px]` or `text-xs` |
| Tiny text | 9-10px | `text-[9px] sm:text-[10px]` |

---

## 8. RESPONSIVE BREAKPOINTS

| Breakpoint | Prefix | Usage |
|------------|--------|-------|
| Mobile | (default) | Base styles |
| Small | `sm:` | 640px+ |
| Medium | `md:` | 768px+ (show sidebar) |
| Large | `lg:` | 1024px+ (4-col grid) |

### Mobile Adaptations
- Sidebar hidden, hamburger menu shown
- Reduced padding: `p-3` → `p-5` on desktop
- Smaller text: `text-[10px]` → `text-xs` on desktop
- 2-column grids → 4-column on large screens

---

## 9. FEATURES TO IMPLEMENT

### High Priority
1. **Glass card styling** - Add glassmorphism effect
2. **Activity feed** - Real-time trade events
3. **Auto-placement monitor** - Background order placement
4. **Status filtering** - Filter trades by status

### Medium Priority
1. **Multi-account support** - Trade across multiple accounts
2. **Unrealized PnL display** - Show live PnL
3. **Better mobile nav** - Hamburger menu

### Low Priority
1. **Version display** - Show version in sidebar
2. **Last sync time** - Show when data was last fetched

---

## 10. COMPARISON WITH OUR TERMINAL

| Feature | Reference | Ours | Action |
|---------|-----------|------|--------|
| Framework | Next.js | Next.js | ✓ Same |
| Styling | Tailwind | Tailwind | ✓ Same |
| Chart | Lightweight Charts | TradingView Embed | **UPGRADE** |
| Color scheme | Amber/Dark | Teal/Dark | Consider |
| Sidebar | 224px, collapsible | 280px, fixed | Adjust |
| Activity feed | Yes | No | **ADD** |
| Auto-monitor | Yes | No | **ADD** |
| Multi-account | Yes | No | Future |
| Status badges | Colored | Basic | **IMPROVE** |

---

## 11. CSS CLASSES TO COPY

```css
/* Glass card effect (needs to be defined) */
.glass-card {
  background: rgba(20, 25, 34, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(30, 37, 48, 0.5);
}

/* Pulse animation for live indicator */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 12. CHART PAGE DEEP DIVE

### 12.1 Page Structure
```html
<div class="space-y-4 sm:space-y-6">
  <!-- Header row -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-100">Positions Chart</h1>
      <p class="text-gray-400 mt-1 text-sm sm:text-base hidden sm:block">
        Visualize your active trades with entry, TP, SL, and rebuy levels
      </p>
    </div>
    <!-- Active positions badge -->
    <div class="flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-emerald-500/10
                border border-emerald-500/20 rounded backdrop-blur-sm self-start">
      <svg class="lucide lucide-activity w-4 sm:w-5 h-4 sm:h-5 text-emerald-400">...</svg>
      <span class="font-semibold text-gray-100 text-sm sm:text-base">5 Active</span>
    </div>
  </div>

  <!-- Chart container -->
  <div class="glass-card rounded overflow-hidden h-[700px]">...</div>

  <!-- Legend -->
  <div class="glass-card rounded p-4">...</div>
</div>
```

### 12.2 Chart Container Structure
```html
<div class="glass-card rounded overflow-hidden h-[700px]">
  <div class="relative flex flex-col h-full">
    <!-- Toolbar -->
    <div class="flex items-center justify-between px-4 py-3 bg-gray-800/50 border-b border-gray-700/50">
      <!-- Left: Symbol selector + current symbol -->
      <div class="flex items-center gap-3">
        <select class="px-3 py-1.5 bg-gray-700/50 border border-gray-600/50 rounded
                       text-gray-200 text-sm font-medium hover:bg-gray-700 transition-colors
                       focus:outline-none focus:ring-2 focus:ring-amber-500/50">
          <option value="ONDO">ONDO/USDT (1)</option>
          <option value="SOL">SOL/USDT (1)</option>
          <!-- Shows count of trades per symbol -->
        </select>
        <div class="text-lg font-bold text-gray-50">BTCUSDT</div>
      </div>

      <!-- Right: Timeframe buttons -->
      <div class="flex items-center gap-2">
        <button class="px-3 py-1.5 rounded text-xs font-semibold transition-all
                       bg-gray-700/30 border border-gray-600/30 text-gray-400 hover:bg-gray-700/50">1m</button>
        <button class="px-3 py-1.5 rounded text-xs font-semibold transition-all
                       bg-amber-500/20 border border-amber-500/30 text-amber-400">1h</button>
        <!-- Active state uses amber -->
      </div>
    </div>

    <!-- Chart area -->
    <div class="relative flex-1">
      <div class="w-full h-full">
        <div class="tv-lightweight-charts" style="...">
          <!-- Canvas layers -->
        </div>
      </div>
    </div>
  </div>
</div>
```

### 12.3 TradingView Lightweight Charts Implementation

**Canvas Structure:**
```html
<div class="tv-lightweight-charts" style="overflow: hidden; direction: ltr;
     width: 1572px; height: 638px; user-select: none; -webkit-tap-highlight-color: transparent;">
  <table cellspacing="0" style="height: 638px; width: 1572px;">
    <tr>
      <td></td>
      <!-- Main chart area (2 canvas layers) -->
      <td style="width: 1472px; height: 610px;">
        <div style="position: relative; overflow: hidden;">
          <canvas style="z-index: 1;" width="2944" height="1220"></canvas>  <!-- Main chart -->
          <canvas style="z-index: 2;" width="2944" height="1220"></canvas>  <!-- Overlay (lines) -->
        </div>
        <!-- TradingView attribution logo -->
        <a href="https://www.tradingview.com/..." id="tv-attr-logo">...</a>
      </td>
      <!-- Price axis (2 canvas layers) -->
      <td style="width: 100px; height: 610px;">
        <canvas style="z-index: 1;" width="200" height="1220"></canvas>
        <canvas style="z-index: 2;" width="200" height="1220"></canvas>
      </td>
    </tr>
    <tr>
      <td></td>
      <!-- Time axis -->
      <td style="height: 28px; width: 1472px;">
        <canvas style="z-index: 1;" width="2944" height="56"></canvas>
        <canvas style="z-index: 2;" width="2944" height="56"></canvas>
      </td>
      <!-- Corner cell -->
      <td style="width: 100px; height: 28px;">...</td>
    </tr>
  </table>
</div>
```

**Key Observations:**
- Uses 2x resolution canvas (2944x1220 for 1472x610 display) - Retina support
- Dual canvas layers: z-index 1 for main chart, z-index 2 for overlays (order lines)
- Price axis is 100px wide
- Time axis is 28px tall
- Table-based layout for precise positioning

### 12.4 Timeframe Buttons
| Timeframe | Button Text |
|-----------|-------------|
| 1 minute | `1m` |
| 5 minutes | `5m` |
| 15 minutes | `15m` |
| 1 hour | `1h` (default active) |
| 4 hours | `4h` |
| 1 day | `1D` |

**Button States:**
```html
<!-- Inactive -->
<button class="px-3 py-1.5 rounded text-xs font-semibold transition-all
               bg-gray-700/30 border border-gray-600/30 text-gray-400 hover:bg-gray-700/50">

<!-- Active -->
<button class="px-3 py-1.5 rounded text-xs font-semibold transition-all
               bg-amber-500/20 border border-amber-500/30 text-amber-400">
```

### 12.5 Chart Legend
```html
<div class="glass-card rounded p-4">
  <h3 class="text-sm font-semibold text-gray-300 mb-3">Chart Legend</h3>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
    <!-- Entry Price - Blue dashed -->
    <div class="flex items-center gap-2">
      <div class="w-8 h-0.5 bg-blue-500 border-2 border-dashed border-blue-500"></div>
      <span class="text-gray-400">Entry Price</span>
    </div>

    <!-- Take Profit - Emerald solid -->
    <div class="flex items-center gap-2">
      <div class="w-8 h-0.5 bg-emerald-500"></div>
      <span class="text-gray-400">Take Profit</span>
    </div>

    <!-- Stop Loss - Red solid -->
    <div class="flex items-center gap-2">
      <div class="w-8 h-0.5 bg-red-500"></div>
      <span class="text-gray-400">Stop Loss</span>
    </div>

    <!-- Rebuy Levels - Orange dotted -->
    <div class="flex items-center gap-2">
      <div class="w-8 h-0.5 bg-orange-500 border-2 border-dotted border-orange-500"></div>
      <span class="text-gray-400">Rebuy Levels</span>
    </div>
  </div>
</div>
```

### 12.6 Order Line Colors (for implementation)
| Line Type | Color | Style |
|-----------|-------|-------|
| Entry Price | `blue-500` (#3b82f6) | Dashed |
| Take Profit | `emerald-500` (#10b981) | Solid |
| Stop Loss | `red-500` (#ef4444) | Solid |
| Rebuy Levels | `orange-500` (#f97316) | Dotted |

### 12.7 Symbol Dropdown
Shows active trades grouped by symbol with count:
```html
<select class="px-3 py-1.5 bg-gray-700/50 border border-gray-600/50 rounded
               text-gray-200 text-sm font-medium">
  <option value="ONDO">ONDO/USDT (1)</option>
  <option value="SOL">SOL/USDT (1)</option>
  <option value="XRP">XRP/USDT (1)</option>
  <option value="TRX">TRX/USDT (1)</option>
  <option value="BNB">BNB/USDT (1)</option>
</select>
```

---

## 13. LIGHTWEIGHT CHARTS IMPLEMENTATION GUIDE

### NPM Package
```bash
npm install lightweight-charts
```

### Basic Setup
```typescript
import { createChart, ColorType, LineStyle } from 'lightweight-charts';

const chart = createChart(container, {
  width: containerWidth,
  height: containerHeight,
  layout: {
    background: { type: ColorType.Solid, color: '#06080c' },
    textColor: '#d1d4dc',
  },
  grid: {
    vertLines: { color: '#1e2530' },
    horzLines: { color: '#1e2530' },
  },
  rightPriceScale: {
    borderColor: '#1e2530',
  },
  timeScale: {
    borderColor: '#1e2530',
  },
});

// Add candlestick series
const candlestickSeries = chart.addCandlestickSeries({
  upColor: '#10b981',      // emerald-500
  downColor: '#ef4444',    // red-500
  borderUpColor: '#10b981',
  borderDownColor: '#ef4444',
  wickUpColor: '#10b981',
  wickDownColor: '#ef4444',
});

// Set data
candlestickSeries.setData(ohlcData);
```

### Adding Price Lines (Order Levels)
```typescript
// Entry line (blue, dashed)
candlestickSeries.createPriceLine({
  price: entryPrice,
  color: '#3b82f6',
  lineWidth: 2,
  lineStyle: LineStyle.Dashed,
  axisLabelVisible: true,
  title: 'Entry',
});

// Take Profit line (emerald, solid)
candlestickSeries.createPriceLine({
  price: tpPrice,
  color: '#10b981',
  lineWidth: 2,
  lineStyle: LineStyle.Solid,
  axisLabelVisible: true,
  title: 'TP1',
});

// Stop Loss line (red, solid)
candlestickSeries.createPriceLine({
  price: slPrice,
  color: '#ef4444',
  lineWidth: 2,
  lineStyle: LineStyle.Solid,
  axisLabelVisible: true,
  title: 'SL',
});

// Rebuy line (orange, dotted)
candlestickSeries.createPriceLine({
  price: rebuyPrice,
  color: '#f97316',
  lineWidth: 1,
  lineStyle: LineStyle.Dotted,
  axisLabelVisible: true,
  title: 'Rebuy 1',
});
```

### WebSocket Data Feed (BingX)
```typescript
// Connect to BingX WebSocket
const ws = new WebSocket('wss://open-api-swap.bingx.com/swap-market');

ws.onopen = () => {
  ws.send(JSON.stringify({
    id: 'kline',
    reqType: 'sub',
    dataType: `market.kline.${symbol}.${interval}`,
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update chart with new candle
  candlestickSeries.update({
    time: data.time / 1000,
    open: parseFloat(data.open),
    high: parseFloat(data.high),
    low: parseFloat(data.low),
    close: parseFloat(data.close),
  });
};
```

---

## 14. TRADES PAGE DEEP DIVE

### 14.1 Page Header
```html
<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
  <div>
    <h1 class="text-xl sm:text-2xl font-semibold text-gray-100 tracking-tight">Trades</h1>
    <p class="text-gray-500 mt-0.5 text-sm hidden sm:block">Manage your trading positions</p>
  </div>

  <!-- Action buttons -->
  <div class="flex items-center gap-2 sm:gap-3">
    <!-- Sync button -->
    <button class="flex items-center gap-1.5 px-3 py-2 bg-amber-500/10 hover:bg-amber-500/15
                   border border-amber-500/30 text-amber-400 rounded text-sm font-medium">
      <svg class="lucide lucide-refresh-cw w-4 h-4">...</svg>
      <span class="hidden sm:inline">Sync</span>
    </button>

    <!-- Open Trade (emerald) -->
    <a class="flex items-center gap-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-500
              text-white rounded text-sm font-medium" href="/trades/open">
      <svg class="lucide lucide-trending-up w-4 h-4">...</svg>
      <span class="hidden sm:inline">Open Trade</span>
    </a>

    <!-- Import (blue) -->
    <a class="flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-500
              text-white rounded text-sm font-medium" href="/trades/new">
      <svg class="lucide lucide-file-braces w-4 h-4">...</svg>
      <span class="hidden sm:inline">Import</span>
    </a>
  </div>
</div>
```

### 14.2 Auto-Placement Monitor Banner
```html
<div class="glass-card rounded p-3 sm:p-4 border-l-2 border-amber-500 bg-amber-500/5">
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <div class="p-2 rounded bg-amber-500/10">
        <svg class="lucide lucide-activity w-4 h-4 text-amber-400">...</svg>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-100">Auto-Placement Monitor</span>
          <span class="px-2 py-0.5 text-[10px] font-semibold rounded bg-amber-500/20 text-amber-400">
            Stopped
          </span>
        </div>
        <div class="flex items-center gap-2 mt-1 text-[11px] text-gray-500">
          <svg class="lucide lucide-circle-alert w-3 h-3 text-amber-400">...</svg>
          <span class="text-amber-400">No pending trades</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 14.3 Filter System
```html
<div class="space-y-3">
  <!-- Status filters -->
  <div>
    <p class="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Status</p>
    <div class="flex flex-wrap gap-2">
      <!-- Active filter -->
      <button class="px-3 py-1.5 rounded text-sm font-medium transition-all
                     bg-gray-600 text-white">
        All<span class="ml-1.5 text-xs opacity-75">(7)</span>
      </button>

      <!-- Inactive filter -->
      <button class="px-3 py-1.5 rounded text-sm font-medium transition-all
                     bg-gray-800/50 text-gray-400 hover:bg-gray-700/50 border border-gray-700/30">
        Pending<span class="ml-1.5 text-xs opacity-75">(0)</span>
      </button>
    </div>
  </div>

  <!-- Type filters -->
  <div>
    <p class="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Type</p>
    <div class="flex flex-wrap gap-2">
      <button class="...">Boxing<span class="ml-1.5 text-xs opacity-75">(7)</span></button>
      <button class="...">Market<span class="ml-1.5 text-xs opacity-75">(0)</span></button>
    </div>
  </div>
</div>
```

**Filter States:**
| State | Classes |
|-------|---------|
| Active | `bg-gray-600 text-white` |
| Inactive | `bg-gray-800/50 text-gray-400 hover:bg-gray-700/50 border border-gray-700/30` |

### 14.4 Trade Card Structure
```html
<div class="glass-card rounded p-5 hover:border-gray-500/30 transition-all duration-300">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-4">
    <div class="space-y-1.5 min-w-0">
      <!-- Symbol row -->
      <div class="flex items-center gap-2 flex-wrap">
        <!-- Coin icon (or fallback) -->
        <img alt="SOL" class="rounded-full flex-shrink-0"
             src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/sol.png"
             style="width: 32px; height: 32px;">

        <!-- Or fallback for unknown coins -->
        <div class="flex items-center justify-center rounded-full bg-amber-500/20
                    border border-gray-600/30" style="width: 32px; height: 32px;">
          <span class="text-[10px] font-bold text-gray-300">ON</span>
        </div>

        <h3 class="text-xl sm:text-2xl font-bold text-gray-100">SOL</h3>

        <!-- Chart button -->
        <button class="p-1.5 rounded bg-amber-500/10 hover:bg-amber-500/20
                       border border-amber-500/30 text-amber-400">
          <svg class="lucide lucide-chart-column w-4 h-4">...</svg>
        </button>

        <!-- Direction badge -->
        <span class="flex items-center gap-1 text-sm font-semibold text-red-400">
          <svg class="lucide lucide-trending-down w-6 h-6">...</svg>
          SHORT
        </span>

        <!-- Type badge -->
        <span class="px-2 py-0.5 text-xs font-semibold rounded-full border
                     bg-purple-500/10 text-purple-400 border-purple-500/30">BOXING</span>
      </div>

      <!-- Price info -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-base sm:text-lg font-bold text-amber-400">$142,38</span>
        <span class="text-sm font-semibold text-red-400">-2.30% to entry</span>
      </div>

      <!-- Trade ID -->
      <p class="text-xs text-gray-500 font-mono truncate">SOL-SHORT-3391a960</p>
    </div>

    <!-- Status badge -->
    <span class="px-3 py-1 text-xs font-semibold rounded-full border whitespace-nowrap
                 bg-amber-500/10 text-amber-400 border-amber-500/30">ACTIVE</span>
  </div>

  <!-- Body: 2-column grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <!-- Left column: Margin, Leverage, Auto-Placement -->
    <!-- Right column: TPs, SL, Entries, Rebuys -->
  </div>

  <!-- Actions -->
  <div class="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-700/30">
    <!-- Buttons -->
  </div>

  <!-- Multi-Account Overview section -->
  <div class="mt-4 p-4 bg-gray-800/30 border border-gray-700/30 rounded">...</div>
</div>
```

### 14.5 Status Badge Colors
| Status | Background | Text | Border |
|--------|-----------|------|--------|
| PENDING | `bg-amber-500/10` | `text-amber-400` | `border-amber-500/30` |
| ACTIVE | `bg-amber-500/10` | `text-amber-400` | `border-amber-500/30` |
| OPEN | `bg-emerald-500/10` | `text-emerald-400` | `border-emerald-500/30` |
| CLOSED | `bg-gray-500/10` | `text-gray-400` | `border-gray-500/30` |

### 14.6 Direction Badges
```html
<!-- LONG -->
<span class="flex items-center gap-1 text-sm font-semibold text-emerald-400">
  <svg class="lucide lucide-trending-up w-6 h-6">...</svg>
  LONG
</span>

<!-- SHORT -->
<span class="flex items-center gap-1 text-sm font-semibold text-red-400">
  <svg class="lucide lucide-trending-down w-6 h-6">...</svg>
  SHORT
</span>
```

### 14.7 Order Level Badges
```html
<!-- Take Profit (unfilled) -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
  TP1: $144,784 (25%)
</div>

<!-- Stop Loss -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-red-500/10 border-red-500/30 text-red-400">
  SL: $161,599
</div>

<!-- Entry (unfilled) -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-amber-500/10 border-amber-500/30 text-amber-400">
  Entry: $145,737 ($16,13)
</div>

<!-- Entry (filled - with checkmark) -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-amber-500/10 border-amber-500/40 text-amber-400">
  <span class="text-amber-400 font-bold text-sm">✓ </span>
  Entry: $2,344 ($16,13)
</div>

<!-- Rebuy (unfilled) -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-orange-500/10 border-orange-500/30 text-orange-400">
  RB1: $147,862 ($32,26)
</div>

<!-- Rebuy (filled) -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-amber-500/10 border-amber-500/40 text-amber-400">
  <span class="text-amber-400 font-bold text-sm">✓ </span>
  RB1: $2,4005 ($32,26)
</div>

<!-- Closed/inactive entry -->
<div class="px-2.5 py-1 border rounded text-xs font-medium flex items-center gap-1.5
            bg-amber-500/10 border-amber-500/20 text-amber-400/50">
  Entry: $2.960,11 ($33,33)
</div>
```

### 14.8 Action Buttons by Status

**PENDING status:**
```html
<button class="... bg-amber-500/10 border-amber-500/30 text-amber-400">Edit</button>
<button class="... bg-emerald-600 text-white">Deploy</button>
<button class="... bg-gray-500/10 border-gray-500/30 text-gray-400">Delete</button>
```

**ACTIVE status:**
```html
<button class="... bg-amber-500/10 border-amber-500/30 text-amber-400">Edit</button>
<button class="... bg-amber-500/10 border-amber-500/30 text-amber-400">Reset</button>
<button class="... bg-gradient-to-r from-red-600 to-orange-600 text-white">Close</button>
<button class="... bg-gray-500/10 border-gray-500/30 text-gray-400">Delete</button>
```

**OPEN status:**
```html
<button class="... bg-amber-500/10 border-amber-500/30 text-amber-400">Edit</button>
<button class="... bg-emerald-500/10 border-emerald-500/30 text-emerald-400">Set TP/SL</button>
<button class="... bg-gradient-to-r from-red-600 to-orange-600 text-white">Close</button>
```

**CLOSED status:**
```html
<button class="... bg-gray-500/10 border-gray-500/30 text-gray-400">Delete</button>
```

### 14.9 Inline Edit Buttons
```html
<button class="flex items-center gap-1 px-2 py-1 text-xs
               bg-gray-700/30 hover:bg-gray-700/50 border border-gray-600/30
               text-gray-300 hover:text-amber-400 rounded transition-all">
  <svg class="lucide lucide-pen w-3 h-3">...</svg>
  Edit
</button>
```

### 14.10 Multi-Account Overview Section
```html
<div class="mt-4 p-4 bg-gray-800/30 border border-gray-700/30 rounded space-y-4">
  <div class="flex items-center justify-between">
    <h4 class="text-sm font-semibold text-gray-300 uppercase">Multi-Account Overview</h4>
    <button class="p-1.5 hover:bg-amber-500/10 rounded">
      <svg class="lucide lucide-refresh-cw w-4 h-4 text-amber-400">...</svg>
    </button>
  </div>

  <!-- Not deployed state -->
  <div class="p-4 bg-amber-500/10 border border-amber-500/20 rounded">
    <p class="text-sm text-amber-400 mb-2">This trade has not been deployed to any accounts yet.</p>
    <button class="flex items-center gap-2 px-3 py-1 bg-blue-500/10 text-blue-400
                   border border-blue-500/20 rounded text-sm hover:bg-blue-500/20">
      Deploy to Account
    </button>
  </div>

  <p class="text-[10px] text-gray-500 text-center">
    Updated: <span class="text-amber-400">16:50:43</span>
  </p>
</div>
```

### 14.11 Coin Icon Sources
```html
<!-- Known coins use jsdelivr CDN -->
<img src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/sol.png">
<img src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/eth.png">
<img src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/xrp.png">
<img src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/trx.png">
<img src="https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/bnb.png">

<!-- Unknown coins show initials -->
<div class="flex items-center justify-center rounded-full bg-amber-500/20
            border border-gray-600/30" style="width: 32px; height: 32px;">
  <span class="text-[10px] font-bold text-gray-300">ON</span>
</div>
```

### 14.12 Close Button (Gradient)
```html
<button class="flex-1 min-w-[100px] flex items-center justify-center gap-1.5 px-3 py-2
               bg-gradient-to-r from-red-600 to-orange-600 text-white rounded
               text-sm font-semibold disabled:opacity-50">
  <svg class="lucide lucide-x w-4 h-4">...</svg>
  Close
</button>
```

### 14.13 Trade Types
| Type | Badge Color |
|------|-------------|
| BOXING | `bg-purple-500/10 text-purple-400 border-purple-500/30` |
| MARKET | Would be different |

### 14.14 Key Features Observed
1. **Live price display** with percentage to entry
2. **Filled order indicators** (✓ checkmark)
3. **Inline edit buttons** for TP/SL/Entries/Rebuys
4. **Multi-account deployment** system
5. **Auto-placement monitor** toggle
6. **Trade type filtering** (Boxing vs Market)
7. **Status-based action buttons**
8. **Coin icons from CDN** with fallback
9. **Trade ID display** (Symbol-Direction-Hash format)

---

## 15. FEATURES COMPARISON - UPDATED

| Feature | Reference Terminal | Our Terminal | Priority |
|---------|-------------------|--------------|----------|
| Lightweight Charts | ✓ | ✗ (embed widget) | **HIGH** |
| Order lines on chart | ✓ | ✗ | **HIGH** |
| Multi-account support | ✓ | ✗ | Medium |
| Auto-placement monitor | ✓ | ✗ | Medium |
| Inline TP/SL editing | ✓ | ✗ | **HIGH** |
| Filled order indicators | ✓ | Partial | Medium |
| Coin icons from CDN | ✓ | ✗ | Low |
| Trade type filtering | ✓ (Boxing/Market) | ✗ | Low |
| Deploy to account | ✓ | ✗ | Medium |
| Gradient close button | ✓ | ✗ | Low |
| Trade ID format | ✓ (SYMBOL-DIR-HASH) | ✗ | Low |
| Glass card styling | ✓ | Partial | Medium |

---

## 16. DASHBOARD PAGE DEEP DIVE

### 16.1 Stat Cards Grid (4 columns)
```html
<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
  <!-- Each stat card -->
  <div class="glass-card rounded p-3 sm:p-5">
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <p class="text-[10px] sm:text-xs text-gray-500 font-medium uppercase tracking-wide">Trades</p>
        <p class="text-xl sm:text-2xl font-semibold text-gray-100 mt-1 font-mono">7</p>
        <div class="flex flex-wrap gap-x-2 gap-y-0.5 mt-1.5 sm:mt-2 text-[10px] sm:text-[11px]">
          <span class="text-amber-400">0 pend</span>
          <span class="text-blue-400">3 act</span>
          <span class="text-emerald-400">2 open</span>
        </div>
      </div>
      <div class="p-2 sm:p-2.5 bg-amber-500/10 rounded flex-shrink-0">
        <svg class="lucide lucide-trending-up w-4 sm:w-5 h-4 sm:h-5 text-amber-500">...</svg>
      </div>
    </div>
  </div>
</div>
```

**Stat Card Types:**
| Card | Icon | Icon Color | Sub-stats |
|------|------|------------|-----------|
| Trades | trending-up | amber-500 | pend/act/open counts |
| Accounts | wallet | emerald-500 | None |
| Unrealized | activity | blue-500 | Position count |
| Multi-Acc | users | violet-500 | tr/act counts |

### 16.2 Auto-Placement Monitor Component
```html
<div class="glass-card rounded p-4 sm:p-5">
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
    <div class="flex items-center gap-3">
      <div class="p-2.5 bg-violet-500/10 rounded">
        <svg class="lucide lucide-activity w-5 h-5 text-violet-400">...</svg>
      </div>
      <div>
        <h2 class="text-sm font-semibold text-gray-100">Auto-Placement Monitor</h2>
        <div class="flex flex-wrap items-center gap-2 mt-1 text-[11px] text-gray-500">
          <span>Checks every 60s</span>
          <span>•</span>
          <span>Last: just now</span>
        </div>
      </div>
    </div>
    <!-- Status badge -->
    <span class="px-2.5 py-1 text-[10px] font-semibold rounded
                bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">RUNNING</span>
  </div>

  <!-- Action buttons -->
  <div class="flex flex-wrap gap-2">
    <button class="flex items-center gap-1.5 px-3 py-2 bg-red-500/10 hover:bg-red-500/20
                   border border-red-500/30 text-red-400 rounded text-sm font-medium">
      <svg class="lucide lucide-square w-4 h-4">...</svg>
      Stop
    </button>
    <button class="flex items-center gap-1.5 px-3 py-2 bg-amber-500/10 hover:bg-amber-500/20
                   border border-amber-500/30 text-amber-400 rounded text-sm font-medium">
      <svg class="lucide lucide-refresh-cw w-4 h-4">...</svg>
      Check Now
    </button>
  </div>
</div>
```

### 16.3 Trade Status Grid (Clickable Cards)
```html
<div class="glass-card rounded p-3 sm:p-5">
  <h2 class="text-xs sm:text-sm font-semibold text-gray-200 mb-3 sm:mb-4 uppercase tracking-wide">
    Trade Status
  </h2>
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
    <!-- Pending -->
    <a class="group" href="/trades?filter=pending">
      <div class="p-2.5 sm:p-3 bg-amber-500/5 border border-amber-500/20 rounded
                  hover:border-amber-500/40 transition-all">
        <p class="text-[9px] sm:text-[10px] text-gray-500 uppercase font-medium tracking-wide">Pending</p>
        <p class="text-lg sm:text-xl font-semibold text-amber-400 mt-0.5 sm:mt-1 font-mono">0</p>
        <p class="text-[9px] sm:text-[10px] text-gray-600 mt-0.5 hidden sm:block">Orders not placed</p>
      </div>
    </a>

    <!-- Active -->
    <a class="group" href="/trades?filter=active">
      <div class="p-2.5 sm:p-3 bg-blue-500/5 border border-blue-500/20 rounded
                  hover:border-blue-500/40 transition-all">
        <p class="...">Active</p>
        <p class="... text-blue-400">3</p>
        <p class="...">Orders placed</p>
      </div>
    </a>

    <!-- Open -->
    <a class="group" href="/trades?filter=open">
      <div class="p-2.5 sm:p-3 bg-emerald-500/5 border border-emerald-500/20 rounded
                  hover:border-emerald-500/40 transition-all">
        <p class="...">Open</p>
        <p class="... text-emerald-400">2</p>
        <p class="...">Position active</p>
      </div>
    </a>

    <!-- Closed -->
    <a class="group" href="/trades?filter=closed">
      <div class="p-2.5 sm:p-3 bg-gray-500/5 border border-gray-600/20 rounded
                  hover:border-gray-500/40 transition-all">
        <p class="...">Closed</p>
        <p class="... text-gray-400">2</p>
        <p class="...">Position closed</p>
      </div>
    </a>
  </div>
</div>
```

### 16.4 Quick Actions Grid
```html
<div class="glass-card rounded p-3 sm:p-5">
  <h2 class="text-xs sm:text-sm font-semibold text-gray-200 mb-3 sm:mb-4 uppercase tracking-wide">
    Quick Actions
  </h2>
  <div class="grid grid-cols-2 gap-2 sm:gap-3">
    <!-- Import Trade -->
    <a class="flex items-center gap-2 sm:gap-3 p-2.5 sm:p-3 bg-amber-500/5 border border-amber-500/20
              hover:border-amber-500/40 rounded transition-all group" href="/trades/new">
      <div class="p-1.5 sm:p-2 bg-amber-500/10 rounded flex-shrink-0">
        <svg class="lucide lucide-plus w-3.5 sm:w-4 h-3.5 sm:h-4 text-amber-400">...</svg>
      </div>
      <div class="min-w-0">
        <p class="font-medium text-gray-100 text-xs sm:text-sm truncate">Import Trade</p>
        <p class="text-[10px] sm:text-[11px] text-gray-500 hidden sm:block">Import from JSON</p>
      </div>
    </a>

    <!-- Add Account -->
    <a class="flex items-center gap-2 sm:gap-3 p-2.5 sm:p-3 bg-emerald-500/5 border border-emerald-500/20
              hover:border-emerald-500/40 rounded transition-all group" href="/accounts">
      <div class="p-1.5 sm:p-2 bg-emerald-500/10 rounded flex-shrink-0">
        <svg class="lucide lucide-wallet w-3.5 sm:w-4 h-3.5 sm:h-4 text-emerald-400">...</svg>
      </div>
      <div class="min-w-0">
        <p class="font-medium text-gray-100 text-xs sm:text-sm truncate">Add Account</p>
        <p class="text-[10px] sm:text-[11px] text-gray-500 hidden sm:block">Add API keys</p>
      </div>
    </a>
  </div>
</div>
```

### 16.5 Activity Feed
```html
<div class="glass-card rounded p-3 sm:p-5">
  <h2 class="text-xs sm:text-sm font-semibold text-gray-200 mb-3 sm:mb-4 uppercase tracking-wide">
    Recent Activity
  </h2>
  <div class="space-y-2">
    <!-- Activity item (clickable) -->
    <div class="bg-gray-800/30 border border-gray-700/30 rounded overflow-hidden">
      <div class="flex items-start gap-3 p-2.5 sm:p-3 cursor-pointer hover:bg-gray-800/50 transition-all group">
        <!-- Icon -->
        <div class="p-1.5 rounded bg-gray-700/50 flex-shrink-0 mt-0.5">
          <svg class="lucide lucide-shield w-3.5 h-3.5 text-emerald-400">...</svg>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-medium text-emerald-400">TP/SL Set</span>
            <a class="text-xs font-mono text-gray-300 hover:text-amber-400" href="/trades/...">ONDO</a>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400">SHORT</span>
          </div>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-[10px] sm:text-[11px] text-gray-500 truncate">→ BingX Test</span>
            <span class="text-[10px] text-gray-600">• click for details</span>
          </div>
        </div>

        <!-- Date -->
        <span class="text-[10px] text-gray-600 flex-shrink-0">5.1.2026</span>
      </div>
    </div>

    <!-- Activity item (non-clickable / in-progress) -->
    <div class="bg-gray-800/30 border border-gray-700/30 rounded overflow-hidden">
      <div class="flex items-start gap-3 p-2.5 sm:p-3 transition-all group">
        <!-- No cursor-pointer, no hover effect -->
        <div class="p-1.5 rounded bg-gray-700/50 flex-shrink-0 mt-0.5">
          <svg class="lucide lucide-shield w-3.5 h-3.5 text-amber-400">...</svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-medium text-amber-400">Setting TP/SL</span>
            <!-- ... -->
          </div>
          <!-- No "click for details" hint -->
        </div>
        <span class="text-[10px] text-gray-600 flex-shrink-0">5.1.2026</span>
      </div>
    </div>
  </div>
</div>
```

### 16.6 Activity Event Types
| Event | Icon | Icon Color | Text Color | Clickable |
|-------|------|------------|------------|-----------|
| TP/SL Set | shield | emerald-400 | emerald-400 | Yes |
| Setting TP/SL | shield | amber-400 | amber-400 | No |
| Closed | circle-check-big | emerald-400 | emerald-400 | Yes |
| Closing | arrow-right-left | amber-400 | amber-400 | No |
| Deployed | circle-check-big | emerald-400 | emerald-400 | Yes |
| Placing | clock | amber-400 | amber-400 | No |

**Pattern:**
- Completed actions (emerald) → Clickable with hover effect
- In-progress actions (amber) → Not clickable, no hover effect

### 16.7 Header Sync Button
```html
<button class="flex-shrink-0 flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 sm:py-2
               bg-amber-500/10 hover:bg-amber-500/15 border border-amber-500/30 text-amber-400
               rounded text-xs sm:text-sm font-medium transition-all disabled:opacity-50">
  <svg class="lucide lucide-refresh-cw w-3.5 sm:w-4 h-3.5 sm:h-4">...</svg>
  <span class="hidden xs:inline">Sync</span>
</button>
```

### 16.8 Monitor Status Badges
```html
<!-- Running -->
<span class="px-2.5 py-1 text-[10px] font-semibold rounded
             bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">RUNNING</span>

<!-- Stopped -->
<span class="px-2.5 py-1 text-[10px] font-semibold rounded
             bg-amber-500/20 text-amber-400">Stopped</span>
```

### 16.9 Unrealized PnL Display
```html
<!-- Positive -->
<p class="text-xl sm:text-2xl font-semibold mt-1 font-mono truncate text-emerald-400">$100.65</p>

<!-- Negative (would be) -->
<p class="text-xl sm:text-2xl font-semibold mt-1 font-mono truncate text-red-400">-$50.32</p>
```

---

## 17. SUMMARY OF ALL DOCUMENTED PAGES

| Page | Section | Key Components |
|------|---------|----------------|
| Dashboard | 16 | Stat cards, Auto-placement monitor, Status grid, Quick actions, Activity feed |
| Chart | 12-13 | Lightweight Charts, Timeframe buttons, Symbol dropdown, Legend |
| Trades | 14 | Trade cards, Filters, Order badges, Action buttons, Multi-account section |

---

## 18. ACCOUNTS PAGE DEEP DIVE

### 18.1 Page Structure
```html
<main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 pb-24 md:pb-8">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
    <div>
      <h1 class="text-xl sm:text-2xl font-bold">Connected Accounts</h1>
      <p class="text-gray-400 text-sm mt-1">Manage your exchange API connections</p>
    </div>
    <!-- Add Account Button -->
    <button class="flex items-center justify-center gap-2 px-4 py-2.5
                   bg-amber-500/10 hover:bg-amber-500/15 border border-amber-500/30
                   text-amber-400 rounded-lg text-sm font-medium transition-all w-full sm:w-auto">
      <svg class="lucide lucide-plus w-4 h-4">...</svg>
      Add Account
    </button>
  </div>

  <!-- Account Cards Grid -->
  <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
    <!-- Account Card(s) -->
  </div>
</main>
```

### 18.2 Account Card Structure
```html
<div class="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
  <!-- Header Section -->
  <div class="p-4 sm:p-5 border-b border-gray-800">
    <div class="flex items-start justify-between gap-3">
      <!-- Exchange Info -->
      <div class="flex items-center gap-3">
        <!-- Exchange Logo -->
        <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-gray-700 to-gray-800
                    flex items-center justify-center text-lg sm:text-xl font-bold text-amber-400">
          Bi  <!-- Exchange initials -->
        </div>
        <div>
          <h3 class="font-semibold text-base sm:text-lg">BingX Test</h3>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-xs text-amber-400">BingX</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">TESTNET</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons (top right) -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <!-- Test Connection Button -->
        <button title="Test Connection"
                class="p-2 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-amber-400 transition-colors">
          <svg class="lucide lucide-plug w-4 h-4">...</svg>
        </button>
        <!-- Clean Orders Button -->
        <button title="Clean All Orders"
                class="p-2 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-amber-400 transition-colors">
          <svg class="lucide lucide-broom w-4 h-4">...</svg>
        </button>
        <!-- Edit Button -->
        <button title="Edit"
                class="p-2 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-amber-400 transition-colors">
          <svg class="lucide lucide-pencil w-4 h-4">...</svg>
        </button>
        <!-- Delete Button -->
        <button title="Delete"
                class="p-2 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-red-400 transition-colors">
          <svg class="lucide lucide-trash-2 w-4 h-4">...</svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Wallet Balance Section -->
  <div class="p-4 sm:p-5 border-b border-gray-800 bg-gray-900/30">
    <!-- Balance Grid -->
  </div>

  <!-- Positions Section (Collapsible) -->
  <div class="border-b border-gray-800">
    <!-- Collapsible content -->
  </div>

  <!-- Active Orders Section (Collapsible) -->
  <div>
    <!-- Collapsible content -->
  </div>
</div>
```

### 18.3 Wallet Balance Grid
```html
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
  <!-- Total Balance -->
  <div>
    <p class="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">Total</p>
    <p class="text-sm sm:text-base font-semibold font-mono mt-0.5">$1,086.63</p>
  </div>

  <!-- Available Balance -->
  <div>
    <p class="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">Available</p>
    <p class="text-sm sm:text-base font-semibold font-mono mt-0.5">$1,074.59</p>
  </div>

  <!-- Used Margin -->
  <div>
    <p class="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">Used Margin</p>
    <p class="text-sm sm:text-base font-semibold font-mono mt-0.5">$12.04</p>
  </div>

  <!-- Unrealized PnL -->
  <div>
    <p class="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">Unrealized P&amp;L</p>
    <p class="text-sm sm:text-base font-semibold font-mono mt-0.5 text-emerald-400">$8.24</p>
    <!-- Use text-red-400 for negative -->
  </div>
</div>
```

### 18.4 Collapsible Section Header
```html
<button class="w-full flex items-center justify-between p-3 sm:p-4 hover:bg-gray-800/30 transition-colors">
  <div class="flex items-center gap-2">
    <span class="text-xs sm:text-sm font-medium">Active Positions</span>
    <span class="px-1.5 py-0.5 text-[10px] rounded bg-amber-500/20 text-amber-400">2</span>
  </div>
  <!-- Chevron rotates when expanded -->
  <svg class="lucide lucide-chevron-down w-4 h-4 text-gray-500 transition-transform rotate-180">...</svg>
</button>
```

### 18.5 Position Row
```html
<div class="p-3 sm:p-4 bg-gray-900/20">
  <div class="space-y-3">
    <!-- Single Position -->
    <div class="flex items-center justify-between p-2.5 sm:p-3 bg-gray-800/30 rounded-lg border border-gray-700/30">
      <div class="flex items-center gap-2 sm:gap-3 min-w-0">
        <!-- Coin Icon -->
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full overflow-hidden flex-shrink-0">
          <img src="https://cdn.jsdelivr.net/gh/nicepay-tech/cryptocurrency-icons@main/128/color/ondo.png"
               alt="ONDO" class="w-full h-full object-cover" />
          <!-- Fallback -->
          <div class="hidden w-full h-full bg-gradient-to-br from-amber-500/20 to-amber-600/20
                      flex items-center justify-center text-amber-400 text-xs font-bold">ON</div>
        </div>

        <!-- Position Info -->
        <div class="min-w-0">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="font-medium text-xs sm:text-sm truncate">ONDO/USDT</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400">SHORT</span>
            <span class="text-[10px] px-1 py-0.5 rounded bg-gray-700 text-gray-400">10x</span>
          </div>
          <div class="flex items-center gap-2 sm:gap-3 text-[10px] sm:text-xs text-gray-500 mt-1">
            <span>Size: $5.60</span>
            <span class="hidden xs:inline">Entry: 1.3981</span>
            <span class="hidden sm:inline">Mark: 1.3673</span>
          </div>
        </div>
      </div>

      <!-- PnL Display -->
      <div class="text-right flex-shrink-0 ml-2">
        <p class="text-xs sm:text-sm font-semibold font-mono text-emerald-400">+2.20%</p>
        <p class="text-[10px] sm:text-xs text-emerald-400/70">$0.12</p>
      </div>
    </div>
  </div>
</div>
```

### 18.6 Active Orders Section
```html
<div class="p-3 sm:p-4 bg-gray-900/20">
  <div class="space-y-3">
    <!-- Orders List with Selection -->
    <div class="space-y-2">
      <!-- Order Item (Selectable) -->
      <div class="flex items-center gap-2 p-2 sm:p-2.5 bg-gray-800/30 rounded-lg border border-gray-700/30
                  hover:bg-gray-800/50 cursor-pointer transition-colors">
        <!-- Checkbox -->
        <input type="checkbox" checked=""
               class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-amber-500
                      focus:ring-amber-500/20 focus:ring-offset-0" />

        <!-- Coin Icon -->
        <div class="w-6 h-6 rounded-full overflow-hidden flex-shrink-0">
          <img src="https://cdn.jsdelivr.net/gh/nicepay-tech/cryptocurrency-icons@main/128/color/xrp.png"
               alt="XRP" class="w-full h-full object-cover" />
        </div>

        <!-- Order Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5">
            <span class="font-medium text-xs truncate">XRP/USDT</span>
            <span class="text-[10px] px-1 py-0.5 rounded bg-emerald-500/10 text-emerald-400">LONG</span>
          </div>
          <div class="flex items-center gap-2 text-[10px] text-gray-500 mt-0.5">
            <span>Limit @ 2.28</span>
            <span>Qty: 1</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Clean Selected Button -->
    <button class="w-full flex items-center justify-center gap-2 px-3 py-2
                   bg-red-500/10 hover:bg-red-500/15 border border-red-500/30
                   text-red-400 rounded-lg text-xs font-medium transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed">
      <svg class="lucide lucide-trash-2 w-3.5 h-3.5">...</svg>
      Cancel Selected (4)
    </button>
  </div>
</div>
```

### 18.7 Account Card Action Buttons
| Button | Icon | Position | Hover Color | Purpose |
|--------|------|----------|-------------|---------|
| Test Connection | plug | Top right | amber-400 | Test API connectivity |
| Clean Orders | broom | Top right | amber-400 | Cancel all open orders |
| Edit | pencil | Top right | amber-400 | Edit account settings |
| Delete | trash-2 | Top right | red-400 | Remove account |

### 18.8 Exchange Logo/Avatar Pattern
```html
<!-- Exchange initials avatar -->
<div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-gray-700 to-gray-800
            flex items-center justify-center text-lg sm:text-xl font-bold text-amber-400">
  Bi  <!-- First 2 chars of exchange name -->
</div>
```

### 18.9 Testnet Badge
```html
<span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">TESTNET</span>
```

### 18.10 Position Direction Badges
```html
<!-- LONG -->
<span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400">LONG</span>

<!-- SHORT -->
<span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400">SHORT</span>
```

### 18.11 Leverage Badge
```html
<span class="text-[10px] px-1 py-0.5 rounded bg-gray-700 text-gray-400">10x</span>
```

### 18.12 Order Selection Checkbox
```html
<input type="checkbox"
       class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-amber-500
              focus:ring-amber-500/20 focus:ring-offset-0" />
```

### 18.13 "No Data" Empty States
```html
<!-- No positions -->
<p class="text-xs text-gray-500 p-3 sm:p-4">No active positions</p>

<!-- No orders -->
<p class="text-xs text-gray-500 p-3 sm:p-4">No active orders</p>
```

### 18.14 Cryptocurrency Icon CDN Pattern
```javascript
// Primary icon URL
const iconUrl = `https://cdn.jsdelivr.net/gh/nicepay-tech/cryptocurrency-icons@main/128/color/${symbol.toLowerCase()}.png`;

// Fallback: 2-char initial avatar
const fallback = symbol.substring(0, 2).toUpperCase();
```

### 18.15 Multiple Accounts Layout
- Uses `xl:grid-cols-2` for 2 columns on extra-large screens
- Single column on smaller screens
- Each account is a self-contained card with all its data

### 18.16 Key Styling Tokens
| Element | Classes |
|---------|---------|
| Card background | `bg-[#161b22]` |
| Card border | `border border-gray-800` |
| Section separator | `border-b border-gray-800` |
| Balance section bg | `bg-gray-900/30` |
| Expanded section bg | `bg-gray-900/20` |
| Position card | `bg-gray-800/30 border border-gray-700/30` |
| Label text | `text-gray-500 uppercase tracking-wide` |
| Mono numbers | `font-mono` |

---

## 19. OPEN TRADE PAGE DEEP DIVE (`/trades/open`)

### 19.1 Page Header
```html
<div>
  <h1 class="text-2xl sm:text-3xl font-bold text-gray-100">Open Market Trade</h1>
  <p class="text-gray-400 mt-1 text-sm sm:text-base">Execute instant market orders with leverage</p>
</div>
```

### 19.2 Page Layout
- 2-column grid on large screens (`lg:grid-cols-2`)
- Each section in a `glass-card` component
- Form-based with sliders for numeric inputs

### 19.3 Token Selector
```html
<div class="glass-card rounded p-4">
  <div class="flex items-center gap-3 mb-3">
    <img src="https://assets.coincap.io/assets/icons/btc@2x.png" alt="BTC" class="w-8 h-8 rounded-full">
    <h2 class="text-sm font-bold text-gray-100">Select Token</h2>
  </div>
  <div class="space-y-2">
    <!-- Search input -->
    <input type="text" placeholder="Search token..."
           class="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded
                  text-gray-100 placeholder-gray-500 focus:outline-none focus:border-amber-500">

    <!-- Token dropdown -->
    <select class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded
                   text-gray-100 focus:outline-none focus:border-amber-500 font-semibold">
      <option value="BTC" selected>BTC</option>
      <option value="ETH">ETH</option>
      <option value="SOL">SOL</option>
      <!-- ... 90+ tokens available -->
    </select>
  </div>
</div>
```

**Token Icon Source:**
```
https://assets.coincap.io/assets/icons/{symbol}@2x.png
```

### 19.4 Direction Selector
```html
<div class="glass-card rounded p-4">
  <h2 class="text-sm font-bold text-gray-100 mb-3">Direction</h2>
  <div class="grid grid-cols-2 gap-2">
    <!-- Active LONG button -->
    <button type="button"
            class="flex items-center justify-center gap-2 px-4 py-3 rounded font-semibold transition-all
                   bg-emerald-600 text-white">
      <svg class="lucide lucide-trending-up w-4 h-4">...</svg>
      LONG
    </button>

    <!-- Inactive SHORT button -->
    <button type="button"
            class="flex items-center justify-center gap-2 px-4 py-3 rounded font-semibold transition-all
                   bg-gray-800 text-gray-400 hover:bg-gray-700">
      <svg class="lucide lucide-trending-down w-4 h-4">...</svg>
      SHORT
    </button>
  </div>
</div>
```

**Direction Button States:**
| Direction | Active | Inactive |
|-----------|--------|----------|
| LONG | `bg-emerald-600 text-white` | `bg-gray-800 text-gray-400 hover:bg-gray-700` |
| SHORT | `bg-red-600 text-white` | `bg-gray-800 text-gray-400 hover:bg-gray-700` |

### 19.5 Margin Selector with Presets
```html
<div class="glass-card rounded p-4">
  <h2 class="text-sm font-bold text-gray-100 mb-3">Margin: $1000</h2>

  <!-- Preset buttons -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
    <button type="button" class="px-2 sm:px-3 py-1.5 text-xs sm:text-sm rounded font-semibold transition-all
                                 bg-gray-800 text-gray-400 hover:bg-gray-700">$100</button>
    <button type="button" class="px-2 sm:px-3 py-1.5 text-xs sm:text-sm rounded font-semibold transition-all
                                 bg-gray-800 text-gray-400 hover:bg-gray-700">$500</button>
    <button type="button" class="px-2 sm:px-3 py-1.5 text-xs sm:text-sm rounded font-semibold transition-all
                                 bg-cyan-500 text-white">$1000</button>  <!-- Active -->
    <button type="button" class="px-2 sm:px-3 py-1.5 text-xs sm:text-sm rounded font-semibold transition-all
                                 bg-gray-800 text-gray-400 hover:bg-gray-700">$2000</button>
  </div>

  <!-- Slider -->
  <input type="range" min="10" max="5000" step="10"
         class="w-full h-2 bg-gray-700 rounded appearance-none cursor-pointer accent-amber-500"
         value="1000">
</div>
```

**Preset Button States:**
| State | Classes |
|-------|---------|
| Active | `bg-cyan-500 text-white` |
| Inactive | `bg-gray-800 text-gray-400 hover:bg-gray-700` |

### 19.6 Leverage Slider
```html
<div class="glass-card rounded p-4">
  <div class="flex items-baseline justify-between mb-3">
    <h2 class="text-sm font-bold text-gray-100">Leverage: 10x</h2>
    <span class="text-xs text-gray-400">$10000.00</span>  <!-- Position size -->
  </div>

  <input type="range" min="1" max="20"
         class="w-full h-2 bg-gray-700 rounded appearance-none cursor-pointer accent-amber-500 mt-8"
         value="10">

  <!-- Scale labels -->
  <div class="flex justify-between text-xs text-gray-1000 mt-2">
    <span>1x</span>
    <span>5x</span>
    <span>10x</span>
    <span>15x</span>
    <span>20x</span>
  </div>
</div>
```

### 19.7 Take Profit Slider
```html
<div class="glass-card rounded p-4">
  <h2 class="text-sm font-bold text-gray-100 mb-3">Take Profit: 5%</h2>
  <input type="range" min="1" max="100"
         class="w-full h-2 bg-gray-700 rounded appearance-none cursor-pointer accent-emerald-500 mt-8"
         value="5">
</div>
```

### 19.8 Stop Loss Slider
```html
<div class="glass-card rounded p-4">
  <h2 class="text-sm font-bold text-gray-100 mb-3">Stop Loss: 3%</h2>
  <input type="range" min="1" max="50"
         class="w-full h-2 bg-gray-700 rounded appearance-none cursor-pointer accent-red-500 mt-8"
         value="3">
</div>
```

### 19.9 Slider Accent Colors
| Slider | Accent Class | Purpose |
|--------|--------------|---------|
| Margin | `accent-amber-500` | Main input |
| Leverage | `accent-amber-500` | Risk multiplier |
| Take Profit | `accent-emerald-500` | Profit target (green) |
| Stop Loss | `accent-red-500` | Loss limit (red) |

### 19.10 Price Summary Cards
```html
<div class="space-y-3">
  <!-- Current Price -->
  <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded">
    <p class="text-gray-400 text-sm">Current Price</p>
    <p class="text-amber-400 font-bold text-xl">$93281.30</p>
  </div>

  <!-- TP/SL Grid -->
  <div class="grid grid-cols-2 gap-3 text-sm">
    <!-- Take Profit Card -->
    <div class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded">
      <p class="text-gray-400 text-xs mb-1">Take Profit</p>
      <p class="text-emerald-400 font-bold text-base">+5%</p>
      <div class="mt-2 space-y-0.5">
        <p class="text-xs text-gray-1000">Price Move: +0.50%</p>
        <p class="text-emerald-300 font-semibold">$93747.71</p>
      </div>
    </div>

    <!-- Stop Loss Card -->
    <div class="p-3 bg-red-500/10 border border-red-500/30 rounded">
      <p class="text-gray-400 text-xs mb-1">Stop Loss</p>
      <p class="text-red-400 font-bold text-base">-3%</p>
      <div class="mt-2 space-y-0.5">
        <p class="text-xs text-gray-1000">Price Move: -0.30%</p>
        <p class="text-red-300 font-semibold">$93001.46</p>
      </div>
    </div>
  </div>
</div>
```

### 19.11 Action Buttons
```html
<div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
  <!-- Cancel Button -->
  <button type="button"
          class="flex-1 px-4 sm:px-6 py-3 bg-gray-800 hover:bg-gray-700 text-gray-100 rounded
                 font-semibold transition-all text-sm sm:text-base">
    Cancel
  </button>

  <!-- Submit Button (dynamic text based on direction) -->
  <button type="submit"
          class="flex-1 px-4 sm:px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white rounded
                 font-semibold shadow-lg shadow-amber-500/20 transition-all disabled:opacity-50
                 text-sm sm:text-base">
    Open LONG
  </button>
</div>
```

### 19.12 Available Tokens (90+ tokens)
```
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, AVAX, LINK, UNI, ATOM, LTC, BCH,
XLM, ALGO, VET, ICP, FIL, HBAR, APT, ARB, OP, SUI, SEI, WLD, TIA, JUP, STRK,
NEAR, IMX, INJ, STX, RUNE, FTM, AAVE, GRT, SNX, MKR, LDO, CRV, COMP, SUSHI, BAL,
YFI, 1INCH, ENJ, MANA, SAND, AXS, GALA, CHZ, FLOW, EOS, XTZ, EGLD, THETA, ZIL,
ONE, KLAY, WAVES, QTUM, ZEC, DASH, ETC, XMR, NEO, IOTA, KSM, CELO, ZEN, BAT,
OMG, ZRX, RVN, SC, DGB, ONT, ICX, NANO, ROSE, ANKR, AUDIO, CVC, SKL, BNT,
STORJ, KNC, REN, LRC, BAND, UMA, NMR, NU, OGN, OXT, RSR, TRB, PAXG
```

### 19.13 Token Icon CDN (CoinCap)
```javascript
// CoinCap assets CDN for token icons
const iconUrl = `https://assets.coincap.io/assets/icons/${symbol.toLowerCase()}@2x.png`;
```

### 19.14 Key Form Features
1. **Live price display** - Current market price in amber
2. **Real-time TP/SL calculation** - Shows target prices based on %
3. **Price move percentage** - Shows actual price movement needed
4. **Position size calculation** - `Margin × Leverage`
5. **Dynamic submit button** - Text changes: "Open LONG" / "Open SHORT"
6. **Slider-based inputs** - User-friendly for mobile
7. **Preset margin buttons** - Quick selection ($100, $500, $1000, $2000)

### 19.15 Form Input Ranges
| Input | Min | Max | Step | Default |
|-------|-----|-----|------|---------|
| Margin | $10 | $5000 | $10 | $1000 |
| Leverage | 1x | 20x | 1 | 10x |
| Take Profit | 1% | 100% | 1 | 5% |
| Stop Loss | 1% | 50% | 1 | 3% |

### 19.16 Calculation Formulas
```javascript
// Position size
const positionSize = margin * leverage;

// TP price (LONG)
const tpPriceMove = takeProfit / leverage;  // 5% TP at 10x = 0.5% price move
const tpPrice = currentPrice * (1 + tpPriceMove / 100);

// SL price (LONG)
const slPriceMove = stopLoss / leverage;  // 3% SL at 10x = 0.3% price move
const slPrice = currentPrice * (1 - slPriceMove / 100);

// For SHORT, reverse the calculations
```

---

## 20. SUMMARY OF ALL DOCUMENTED PAGES

| Page | Section | Key Components |
|------|---------|----------------|
| Dashboard | 16 | Stat cards, Auto-placement monitor, Status grid, Quick actions, Activity feed |
| Chart | 12-13 | Lightweight Charts, Timeframe buttons, Symbol dropdown, Legend |
| Trades | 14 | Trade cards, Filters, Order badges, Action buttons, Multi-account section |
| Accounts | 18 | Account cards, Wallet balances, Positions, Orders list, Select & Clean |
| Open Trade | 19 | Token selector, Direction toggle, Margin/Leverage sliders, TP/SL config |

---

## 22. IMPORT TRADE PAGE (`/trades/new`)

### 22.1 Page Overview
The Import Trade page allows importing JSON trade plans and deploying them to multiple accounts simultaneously. Key features:
- Multi-account selection with checkbox
- Margin allocation presets
- Auto-place price threshold configuration
- JSON file upload with drag and drop

### 22.2 Page Header
```html
<div class="text-center mb-8">
  <h1 class="text-2xl sm:text-3xl font-bold text-gray-100">Import Trade</h1>
  <p class="text-gray-400 mt-2 text-sm sm:text-base">
    Import your trade plan JSON and deploy to selected accounts
  </p>
</div>
```

### 22.3 Account Selection Section
```html
<div class="glass-card rounded-xl p-6 space-y-4">
  <h2 class="text-lg font-semibold text-gray-100 flex items-center gap-2">
    <svg class="w-5 h-5 text-amber-400"><!-- Wallet icon --></svg>
    Select Accounts
  </h2>

  <!-- Account Checkbox Cards -->
  <div class="space-y-3">
    <!-- Account 1 - Selected -->
    <label class="flex items-center gap-4 p-4 bg-[#1a1f2a] border border-amber-500/50 rounded-lg cursor-pointer">
      <input type="checkbox" checked
             class="w-5 h-5 rounded border-gray-600 bg-gray-800 text-amber-500
                    focus:ring-amber-500 focus:ring-offset-gray-900">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <span class="font-medium text-gray-100">BingX Main</span>
          <span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded">Active</span>
        </div>
        <div class="text-sm text-gray-400 mt-1">
          Available: <span class="text-emerald-400">$2,450.00</span>
          <span class="mx-2">|</span>
          Need: <span class="text-amber-400">$500</span>
        </div>
      </div>
    </label>

    <!-- Account 2 - Selected -->
    <label class="flex items-center gap-4 p-4 bg-[#1a1f2a] border border-amber-500/50 rounded-lg cursor-pointer">
      <input type="checkbox" checked
             class="w-5 h-5 rounded border-gray-600 bg-gray-800 text-amber-500">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <span class="font-medium text-gray-100">BTCC Trading</span>
          <span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded">Active</span>
        </div>
        <div class="text-sm text-gray-400 mt-1">
          Available: <span class="text-emerald-400">$1,800.00</span>
          <span class="mx-2">|</span>
          Need: <span class="text-amber-400">$500</span>
        </div>
      </div>
    </label>

    <!-- Account 3 - Insufficient Funds (Not Selected) -->
    <label class="flex items-center gap-4 p-4 bg-[#1a1f2a] border border-gray-700 rounded-lg cursor-pointer opacity-60">
      <input type="checkbox" disabled
             class="w-5 h-5 rounded border-gray-600 bg-gray-800">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <span class="font-medium text-gray-100">Testnet Account</span>
          <span class="px-2 py-0.5 bg-gray-500/20 text-gray-400 text-xs rounded">Testnet</span>
        </div>
        <div class="text-sm text-gray-400 mt-1">
          Available: <span class="text-red-400">$150.00</span>
          <span class="mx-2">|</span>
          Need: <span class="text-amber-400">$500</span>
          <span class="text-red-400 ml-2">(Insufficient)</span>
        </div>
      </div>
    </label>
  </div>

  <!-- Selection Summary -->
  <div class="pt-3 border-t border-gray-800">
    <p class="text-sm text-gray-400">
      Trade will be deployed to <span class="text-amber-400 font-medium">2 accounts</span>
    </p>
  </div>
</div>
```

### 22.4 Account Selection States
| State | Border Color | Checkbox | Opacity |
|-------|--------------|----------|---------|
| Selected | `border-amber-500/50` | Checked | 100% |
| Unselected | `border-gray-700` | Unchecked | 100% |
| Insufficient Funds | `border-gray-700` | Disabled | 60% |
| Hover | `border-amber-500/70` | - | 100% |

### 22.5 Margin Allocation Section
```html
<div class="glass-card rounded-xl p-6 space-y-4">
  <h2 class="text-lg font-semibold text-gray-100 flex items-center gap-2">
    <svg class="w-5 h-5 text-amber-400"><!-- DollarSign icon --></svg>
    Margin Allocation
  </h2>

  <!-- Preset Buttons -->
  <div class="flex gap-3">
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      25%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      50%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      75%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-amber-500/20 text-amber-400 border border-amber-500/50">
      100%
    </button>
  </div>

  <!-- Warning Message -->
  <p class="text-sm text-amber-400/80 flex items-center gap-2">
    <svg class="w-4 h-4"><!-- AlertTriangle icon --></svg>
    The imported trade will use 100% of each account's default margin
  </p>
</div>
```

### 22.6 Margin Allocation Button States
```css
/* Default state */
.margin-btn {
  @apply bg-gray-800 text-gray-300 hover:bg-gray-700;
}

/* Selected state */
.margin-btn-selected {
  @apply bg-amber-500/20 text-amber-400 border border-amber-500/50;
}
```

### 22.7 Auto-Place Price Threshold Section
```html
<div class="glass-card rounded-xl p-6 space-y-4">
  <h2 class="text-lg font-semibold text-gray-100 flex items-center gap-2">
    <svg class="w-5 h-5 text-amber-400"><!-- Target icon --></svg>
    Auto-Place Price Threshold
  </h2>

  <p class="text-sm text-gray-400">
    Orders will auto-execute when price is within threshold of entry level
  </p>

  <!-- Preset Buttons -->
  <div class="flex gap-3">
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-amber-500/20 text-amber-400 border border-amber-500/50">
      1%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      3%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      5%
    </button>
    <button class="flex-1 py-2 px-4 rounded-lg font-medium transition-all
                   bg-gray-800 text-gray-300 hover:bg-gray-700">
      10%
    </button>
  </div>

  <!-- Custom Input (optional) -->
  <div class="flex items-center gap-2">
    <span class="text-gray-400 text-sm">Custom:</span>
    <input type="number" step="0.1" min="0.1" max="20"
           class="w-20 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded
                  text-gray-100 text-sm focus:border-amber-500 focus:outline-none"
           placeholder="0.0">
    <span class="text-gray-400 text-sm">%</span>
  </div>
</div>
```

### 22.8 JSON File Upload Section
```html
<div class="glass-card rounded-xl p-6 space-y-4">
  <h2 class="text-lg font-semibold text-gray-100 flex items-center gap-2">
    <svg class="w-5 h-5 text-amber-400"><!-- Upload icon --></svg>
    Trade Plan JSON
  </h2>

  <!-- Dropzone -->
  <div class="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center
              hover:border-amber-500/50 transition-colors cursor-pointer"
       ondrop="handleDrop(event)" ondragover="handleDragOver(event)">
    <div class="flex flex-col items-center gap-3">
      <div class="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center">
        <svg class="w-6 h-6 text-amber-400"><!-- FileJson icon --></svg>
      </div>
      <div>
        <p class="text-gray-100 font-medium">Drop your JSON file here</p>
        <p class="text-sm text-gray-400 mt-1">or click to browse</p>
      </div>
      <input type="file" accept=".json,application/json" class="hidden" id="fileInput">
    </div>
  </div>

  <!-- File Selected State -->
  <div class="hidden" id="fileSelected">
    <div class="flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
      <svg class="w-5 h-5 text-emerald-400"><!-- CheckCircle icon --></svg>
      <span class="text-emerald-400 font-medium" id="fileName">trade_plan.json</span>
      <button class="ml-auto text-gray-400 hover:text-red-400">
        <svg class="w-4 h-4"><!-- X icon --></svg>
      </button>
    </div>
  </div>
</div>
```

### 22.9 Dropzone States
| State | Border | Background |
|-------|--------|------------|
| Default | `border-gray-700 border-dashed` | Transparent |
| Hover | `border-amber-500/50` | Transparent |
| Drag Over | `border-amber-500 bg-amber-500/5` | Tinted |
| File Selected | Solid green indicator | `bg-emerald-500/10` |

### 22.10 Action Buttons
```html
<div class="flex gap-4 mt-6">
  <button class="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 text-gray-100
                 rounded-lg font-medium transition-all">
    Cancel
  </button>
  <button class="flex-1 px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white
                 rounded-lg font-semibold shadow-lg shadow-amber-500/20
                 transition-all disabled:opacity-50"
          disabled>
    Import & Deploy
  </button>
</div>
```

### 22.11 Import Button States
| State | Style | Action |
|-------|-------|--------|
| Disabled (no file) | `opacity-50`, cursor not-allowed | None |
| Enabled (file + accounts) | Full opacity, amber glow | Submit import |
| Loading | `opacity-75`, spinner | Processing |

### 22.12 Expected JSON Trade Plan Format
```json
{
  "tradeSetup": {
    "symbol": "SOLUSD",
    "direction": "LONG",
    "dateTime": "2024-01-15T10:30:00Z",
    "marginUSD": 500,
    "entryPrice": 185.50,
    "averagePrice": 183.75,
    "stopLoss": 175.00,
    "leverage": 10,
    "maxLossPercent": 5
  },
  "orderEntries": [
    {"label": "Entry", "sizeUSD": 200, "price": 185.50, "average": 185.50},
    {"label": "Rebuy 1", "sizeUSD": 150, "price": 182.00, "average": 184.10},
    {"label": "Rebuy 2", "sizeUSD": 150, "price": 178.50, "average": 182.50}
  ],
  "takeProfits": [
    {"level": "TP1", "price": 195.00, "sizePercent": 25},
    {"level": "TP2", "price": 205.00, "sizePercent": 25},
    {"level": "TP3", "price": 215.00, "sizePercent": 25},
    {"level": "TP4", "price": 225.00, "sizePercent": 25}
  ],
  "notes": "SOL breakout trade"
}
```

### 22.13 Key Import Page Features
1. **Multi-account deployment** - One trade plan → multiple exchanges
2. **Margin scaling** - Adjust allocation per account (25/50/75/100%)
3. **Auto-place threshold** - Don't wait for exact price, execute within range
4. **File validation** - JSON schema validation before import
5. **Balance check** - Disable accounts with insufficient funds
6. **Drag and drop** - Modern file upload UX

---

## 23. VISUAL OBSERVATIONS FROM SCREENSHOTS

### 23.1 Screenshot 1: Dashboard Page
**Key Visual Elements:**
- Clean dark theme with `#0d1117` background
- Amber/gold accent color (`#f59e0b`) throughout
- 4 stat cards in a row: Total Trades, Active, Win Rate, Total P&L
- "Auto-Placement Monitor" widget showing price monitoring status
- Trade status grid with 4 columns of status badges
- Activity feed with timestamps and event descriptions

**Notable UI Patterns:**
- Stat values are large and bold (text-3xl)
- Subtle amber glow on important values
- Icons consistently use amber-400 color
- Glass card effect with slight transparency

### 23.2 Screenshot 2: Trades Page
**Key Visual Elements:**
- Two trade cards visible: ONDO (LONG) and SOL (LONG)
- Each card shows filled entries with checkmarks (✓)
- Price levels clearly displayed with color coding:
  - Entry: amber badge with checkmark
  - Rebuy 1, Rebuy 2: amber badges (filled have checkmark)
  - TP levels: emerald/green badges
  - SL: red badge

**ONDO Trade Card Details:**
```
Symbol: ONDO
Direction: LONG (emerald pill)
Account: BingX Main

Filled Entries (amber with ✓):
- ✓ Entry: $2,344 ($16,13)
- ✓ Rebuy 1: $2,200 ($16,13)
- ✓ Rebuy 2: $2,100 ($16,13)

Take Profits (emerald):
- TP1: $2,450 (25%)
- TP2: $2,550 (25%)
- TP3: $2,650 (25%)
- TP4: $2,750 (25%)

Stop Loss (red):
- SL: $1,950
```

**SOL Trade Card Details:**
```
Symbol: SOL
Direction: LONG (emerald pill)
Account: BTCC Trading

Entries: Entry, Rebuy 1-5
TPs: TP1-TP5
```

### 23.3 Screenshot 3: Open Market Trade Page
**Key Visual Elements:**
- Token selector dropdown at top (showing "BTC")
- LONG/SHORT toggle buttons (LONG selected, emerald color)
- Slider controls for:
  - Margin: $1,000 (with preset buttons: $100, $500, $1000, $2000)
  - Leverage: 10x (scale 1x to 20x)
  - Take Profit: 5% (emerald accent)
  - Stop Loss: 3% (red accent)
- Price summary cards showing calculated TP/SL prices
- Action buttons: Cancel (gray) and Open LONG (amber)

### 23.4 Screenshot 4: Import Trade Page
**Key Visual Elements:**
- "Select Accounts" section with checkboxes
- Account cards showing:
  - Account name and status badge
  - Available balance (emerald) and Required amount (amber)
- "Trade will be deployed to 2 accounts" summary
- Margin Allocation buttons: 25%, 50%, 75%, 100% (100% selected)
- Warning message in amber about margin usage
- Auto-Place Price Threshold: 1%, 3%, 5%, 10% (1% selected)
- JSON file upload dropzone with icon

### 23.5 Screenshot 5: Chart Page with Order Lines
**Critical Visual Information:**
- Uses Lightweight Charts (TradingView's npm package)
- Symbol dropdown: "SOL/USDT (1)" with count indicator
- Timeframe buttons: 1m, 5m, 15m, 1h (active), 4h, 1D
- Candlestick chart with OHLC data

**Order Line Overlays:**
```
VISIBLE LINES ON CHART:
├── Entry Line (BLUE, dashed)
│   └── Label: "Entry $185.50"
├── TP1 (GREEN, solid)
│   └── Label: "TP1 $195.00"
├── TP2 (GREEN, solid)
│   └── Label: "TP2 $205.00"
├── TP3 (GREEN, solid)
│   └── Label: "TP3 $215.00"
├── TP4 (GREEN, solid)
│   └── Label: "TP4 $225.00"
├── TP5 (GREEN, solid)
│   └── Label: "TP5 $235.00"
├── SL Line (RED, solid)
│   └── Label: "SL $175.00"
├── Rebuy 1 (ORANGE, dotted)
│   └── Label: "Rebuy 1 $182.00"
├── Rebuy 2 (ORANGE, dotted)
│   └── Label: "Rebuy 2 $178.50"
└── Rebuy 3 (ORANGE, dotted)
    └── Label: "Rebuy 3 $175.50"
```

**Legend at Bottom:**
- Entry Price (blue square)
- Take Profit (green square)
- Stop Loss (red square)
- Rebuy Levels (orange square)

### 23.6 Screenshot 6: Accounts Page
**Key Visual Elements:**
- Multiple account cards displayed
- Each card shows:
  - Exchange logo/icon
  - Account name (e.g., "BingX Main", "BTCC Trading")
  - Network badge: "Mainnet" (emerald) or "Testnet" (gray)
  - Status: "Active" badge + "Online" indicator (green dot)
  - Default Margin: "$500"
  - Position Mode: "Hedge" or "One-way"

**Account Card Details:**
```html
<div class="glass-card">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-3">
      <img src="exchange-logo.png" class="w-8 h-8 rounded">
      <div>
        <h3 class="font-semibold">BingX Main</h3>
        <span class="badge-emerald">Mainnet</span>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
      <span class="text-emerald-400 text-sm">Online</span>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="grid grid-cols-2 gap-4 mt-4">
    <div>
      <p class="text-gray-400 text-xs">Default Margin</p>
      <p class="text-gray-100 font-medium">$500</p>
    </div>
    <div>
      <p class="text-gray-400 text-xs">Position Mode</p>
      <p class="text-gray-100 font-medium">Hedge</p>
    </div>
  </div>

  <!-- Wallet Balance -->
  <div class="mt-4 p-3 bg-[#1a1f2a] rounded">
    <p class="text-gray-400 text-xs">Available Balance</p>
    <p class="text-emerald-400 font-bold text-xl">$2,450.00</p>
  </div>
</div>
```

### 23.7 Key Visual Design Patterns Confirmed

**Color Palette:**
| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0d1117` | Page background |
| Card Background | `#161b22` | Glass cards |
| Card Border | `#30363d` | Borders |
| Amber (Primary) | `#f59e0b` | Accents, buttons, highlights |
| Emerald (Profit) | `#10b981` | Profits, LONG, positive states |
| Red (Loss) | `#ef4444` | Losses, SHORT, SL, negative states |
| Orange (Warning) | `#f97316` | Rebuy levels, warnings |
| Blue (Info) | `#3b82f6` | Entry levels, informational |

**Typography:**
- Headers: Inter/System UI, bold, gray-100
- Body: Inter/System UI, regular, gray-400
- Monospace: JetBrains Mono for numbers/prices
- Display font: Outfit for large stats

**Component Patterns:**
1. **Glass Cards**: `bg-[#161b22]/80 backdrop-blur border border-gray-800 rounded-xl`
2. **Buttons**: Amber primary, gray secondary, with shadow glow
3. **Badges**: Colored background with matching border at 10-20% opacity
4. **Status Indicators**: Small colored dots with text labels
5. **Sliders**: Full-width with accent colors per type

---

## 24. SUMMARY OF ALL DOCUMENTED PAGES

| Page | Section | Key Components |
|------|---------|----------------|
| Dashboard | 16 | Stat cards, Auto-placement monitor, Status grid, Quick actions, Activity feed |
| Chart | 12-13, 23.5 | Lightweight Charts, Order line overlays, Timeframe buttons, Symbol dropdown |
| Trades | 14, 23.2 | Trade cards with order badges, Status filters, Multi-account section |
| Accounts | 18, 23.6 | Account cards, Wallet balances, Position mode, Online indicators |
| Open Trade | 19, 23.3 | Token selector, Direction toggle, Margin/Leverage sliders, TP/SL config |
| Import Trade | 22, 23.4 | Account selection, Margin allocation, Auto-place threshold, JSON upload |

---

## 25. NEXT STEPS

1. [x] Export HAR file for API endpoints
2. [x] Navigate to `/chart` page and capture that HTML
3. [x] Navigate to `/trades` page and capture the trade list/form
4. [x] Navigate to `/dashboard` page and capture that HTML
5. [x] Navigate to `/accounts` page and capture that HTML
6. [x] Navigate to `/trades/open` page and capture that HTML
7. [x] Capture screenshots of all pages
8. [x] Document Import Trade page (`/trades/new`)
9. [ ] Check Console for WebSocket connections
10. [ ] Implement Lightweight Charts with order line overlays
11. [ ] Add inline TP/SL editing on chart
12. [ ] Add coin icons from CDN
13. [ ] Implement activity feed
14. [ ] Add auto-placement monitor UI
15. [ ] Add account management page with positions/orders display
16. [ ] Add market order page with sliders
17. [ ] Add import trade page with multi-account support
18. [ ] Add trade card filled state indicators (checkmarks)
