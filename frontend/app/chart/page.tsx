"use client";

import { useState, useEffect, useMemo } from "react";
import LightweightChart from "@/components/LightweightChart";
import { api } from "@/lib/api";
import { Trade, TradeStatus } from "@/types";
import { ExternalLink } from "lucide-react";

const TIMEFRAMES = [
  { label: "1m", value: "1m" },
  { label: "5m", value: "5m" },
  { label: "15m", value: "15m" },
  { label: "1h", value: "1h" },
  { label: "4h", value: "4h" },
  { label: "1D", value: "1d" },
];

const POPULAR_SYMBOLS = ["BTC", "ETH", "XRP", "SOL", "DOGE"];

export default function ChartPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const [selectedTradeId, setSelectedTradeId] = useState<number | null>(null);
  const [timeframe, setTimeframe] = useState("1h");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        const data = await api.getTrades();
        setTrades(data);

        // Find the first active or pending trade to show its symbol
        const activeTrade = data.find(
          (t) => t.status === TradeStatus.ACTIVE || t.status === TradeStatus.PENDING || t.status === TradeStatus.OPEN
        );
        if (activeTrade) {
          const baseSymbol = activeTrade.symbol
            .replace("/USDT:USDT", "")
            .replace("USDT", "")
            .replace("/", "")
            .toUpperCase();
          setSelectedSymbol(baseSymbol);
          setSelectedTradeId(activeTrade.id);
        }
      } catch (error) {
        console.error("Failed to fetch trades:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, []);

  // Get active trades (not closed)
  const activeTrades = useMemo(() => {
    return trades.filter((t) => t.status !== TradeStatus.CLOSED);
  }, [trades]);

  // Get trades for the selected symbol
  const tradesForSymbol = useMemo(() => {
    return activeTrades.filter((t) => {
      const baseSymbol = t.symbol
        .replace("/USDT:USDT", "")
        .replace("USDT", "")
        .replace("/", "")
        .toUpperCase();
      return baseSymbol === selectedSymbol;
    });
  }, [activeTrades, selectedSymbol]);

  // Get selected trade
  const selectedTrade = useMemo(() => {
    if (selectedTradeId) {
      return trades.find((t) => t.id === selectedTradeId) || null;
    }
    // Default to first trade for symbol
    return tradesForSymbol[0] || null;
  }, [selectedTradeId, tradesForSymbol, trades]);

  // Get unique symbols from active trades
  const tradeSymbols = useMemo(() => {
    const symbols = new Set<string>();
    activeTrades.forEach((t) => {
      const baseSymbol = t.symbol
        .replace("/USDT:USDT", "")
        .replace("USDT", "")
        .replace("/", "")
        .toUpperCase();
      symbols.add(baseSymbol);
    });
    return Array.from(symbols);
  }, [activeTrades]);

  // Handle symbol change
  const handleSymbolChange = (newSymbol: string) => {
    setSelectedSymbol(newSymbol);
    // Find first trade for this symbol
    const trade = activeTrades.find((t) => {
      const baseSymbol = t.symbol
        .replace("/USDT:USDT", "")
        .replace("USDT", "")
        .replace("/", "")
        .toUpperCase();
      return baseSymbol === newSymbol;
    });
    setSelectedTradeId(trade?.id || null);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-4 py-3 bg-gray-800/50 border-b border-gray-700/50">
          {/* Left: Symbol selector */}
          <div className="flex items-center gap-3">
            <select
              value={selectedSymbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              className="px-3 py-1.5 bg-gray-700/50 border border-gray-600/50 rounded
                         text-gray-200 text-sm font-medium hover:bg-gray-700 transition-colors
                         focus:outline-none focus:ring-2 focus:ring-teal-500/50"
            >
              {/* Show symbols from active trades first */}
              {tradeSymbols.length > 0 && (
                <optgroup label="Your Trades">
                  {tradeSymbols.map((symbol) => {
                    const count = activeTrades.filter((t) => {
                      const base = t.symbol
                        .replace("/USDT:USDT", "")
                        .replace("USDT", "")
                        .replace("/", "")
                        .toUpperCase();
                      return base === symbol;
                    }).length;
                    return (
                      <option key={symbol} value={symbol}>
                        {symbol}/USDT ({count})
                      </option>
                    );
                  })}
                </optgroup>
              )}

              {/* Popular pairs */}
              <optgroup label="Popular Pairs">
                {POPULAR_SYMBOLS.filter((s) => !tradeSymbols.includes(s)).map(
                  (symbol) => (
                    <option key={symbol} value={symbol}>
                      {symbol}/USDT
                    </option>
                  )
                )}
              </optgroup>
            </select>

            {/* Current symbol display */}
            <div className="text-lg font-bold text-gray-50">
              {selectedSymbol}USDT
            </div>

            {/* Trade selector if multiple trades for symbol */}
            {tradesForSymbol.length > 1 && (
              <select
                value={selectedTradeId || ""}
                onChange={(e) => setSelectedTradeId(Number(e.target.value))}
                className="px-2 py-1 bg-gray-700/50 border border-gray-600/50 rounded
                           text-gray-300 text-xs focus:outline-none"
              >
                {tradesForSymbol.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.direction} - {t.status}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Right: Timeframe buttons + TradingView link */}
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-1 sm:gap-2">
              {TIMEFRAMES.map((tf) => (
                <button
                  key={tf.value}
                  onClick={() => setTimeframe(tf.value)}
                  className={`px-2 sm:px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                    timeframe === tf.value
                      ? "bg-teal-500/20 border border-teal-500/30 text-teal-400"
                      : "bg-gray-700/30 border border-gray-600/30 text-gray-400 hover:bg-gray-700/50"
                  }`}
                >
                  {tf.label}
                </button>
              ))}
            </div>

            {/* TradingView link for drawing tools */}
            <a
              href={`https://www.tradingview.com/chart/?symbol=BINGX:${selectedSymbol}USDT.P`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium
                         bg-blue-500/10 border border-blue-500/30 text-blue-400
                         hover:bg-blue-500/20 transition-colors"
              title="Open in TradingView for drawing tools"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">TradingView</span>
            </a>
          </div>
        </div>

        {/* Chart */}
        <div className="flex-1 min-h-0 max-h-[calc(100vh-200px)]">
          <LightweightChart
            symbol={selectedSymbol}
            interval={timeframe}
            trade={selectedTrade}
            className="w-full h-full"
          />
        </div>

        {/* Legend */}
        <div className="px-4 py-2.5 bg-[#0d1117] border-t border-gray-800">
          <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-5 h-0.5 border-t-2 border-dashed border-blue-500" />
              <span className="text-gray-400">Entry</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-0.5 bg-emerald-500" />
              <span className="text-gray-400">Take Profit</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-0.5 bg-red-500" />
              <span className="text-gray-400">Stop Loss</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-0.5 border-t-2 border-dotted border-orange-500" />
              <span className="text-gray-400">Rebuy</span>
            </div>
          </div>
        </div>
    </div>
  );
}
