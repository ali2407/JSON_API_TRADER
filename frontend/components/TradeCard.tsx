"use client";

import { useState } from "react";
import { Trade, TradeDirection } from "@/types";
import { TrendingDown, TrendingUp, RefreshCw, Check, ChartColumn } from "lucide-react";
import Link from "next/link";

interface TradeCardProps {
  trade: Trade;
  onEdit?: (trade: Trade) => void;
  onClose?: (trade: Trade) => void;
  onRefresh?: (trade: Trade) => void;
  onStart?: (trade: Trade) => void;
}

// Get coin icon URL from CDN with fallback
const getCoinIconUrl = (symbol: string): string => {
  const baseSymbol = symbol
    .replace("/USDT:USDT", "")
    .replace("USDT", "")
    .replace("/", "")
    .toLowerCase();
  return `https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/${baseSymbol}.png`;
};

// Extract base symbol for display
const getBaseSymbol = (symbol: string): string => {
  return symbol
    .replace("/USDT:USDT", "")
    .replace("USDT", "")
    .replace("/", "")
    .toUpperCase();
};

export default function TradeCard({ trade, onEdit, onClose, onRefresh, onStart }: TradeCardProps) {
  const [iconError, setIconError] = useState(false);
  const isLong = trade.direction === TradeDirection.LONG;
  const directionColor = isLong ? "text-emerald-400" : "text-red-400";
  const directionBg = isLong ? "bg-emerald-500/10" : "bg-red-500/10";

  const baseSymbol = getBaseSymbol(trade.symbol);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PENDING":
        return "text-amber-400 bg-amber-500/10 border-amber-500/30";
      case "ACTIVE":
        return "text-blue-400 bg-blue-500/10 border-blue-500/30";
      case "OPEN":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      case "CLOSED":
        return "text-gray-400 bg-gray-500/10 border-gray-500/30";
      default:
        return "text-gray-400 bg-gray-500/10 border-gray-500/30";
    }
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) return `$${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    if (price >= 1) return `$${price.toFixed(4)}`;
    return `$${price.toFixed(6)}`;
  };

  const formatUSD = (amount: number) => `$${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

  // Separate entries and rebuys
  const mainEntries = trade.entries.filter(
    (e) => !e.label.toLowerCase().startsWith("rb") && !e.label.toLowerCase().startsWith("rebuy")
  );
  const rebuys = trade.entries.filter(
    (e) => e.label.toLowerCase().startsWith("rb") || e.label.toLowerCase().startsWith("rebuy")
  );

  return (
    <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5 space-y-4 hover:border-gray-700/50 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          {/* Coin Icon */}
          {!iconError ? (
            <img
              src={getCoinIconUrl(trade.symbol)}
              alt={baseSymbol}
              className="w-8 h-8 rounded-full flex-shrink-0"
              onError={() => setIconError(true)}
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-gray-600/30 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-gray-300">
                {baseSymbol.substring(0, 2)}
              </span>
            </div>
          )}

          <h3 className="text-xl sm:text-2xl font-bold truncate">{baseSymbol}</h3>

          {/* Chart link */}
          <Link
            href={`/chart?symbol=${baseSymbol}`}
            className="p-1.5 rounded bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 transition-colors"
            title="View on chart"
          >
            <ChartColumn className="w-4 h-4" />
          </Link>

          {/* Direction badge */}
          <div className={`flex items-center gap-1 px-2 py-1 rounded ${directionBg}`}>
            {isLong ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
            <span className={`text-sm font-semibold ${directionColor}`}>{trade.direction}</span>
          </div>
        </div>

        {/* Status badge */}
        <div className={`px-3 py-1 rounded-full text-xs font-semibold border whitespace-nowrap ${getStatusColor(trade.status)}`}>
          {trade.status}
        </div>
      </div>

      <p className="text-xs text-gray-500 font-mono truncate">{trade.trade_id}</p>

      {/* Trade Details - 2x2 grid */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Margin</p>
          <p className="text-base font-semibold mt-0.5">{formatUSD(trade.margin_usd)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Leverage</p>
          <p className="text-base font-semibold mt-0.5 text-blue-400">{trade.leverage}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Entry</p>
          <p className="text-base font-semibold mt-0.5">{formatPrice(trade.entry_price)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Stop Loss</p>
          <p className="text-base font-semibold mt-0.5 text-red-400">{formatPrice(trade.stop_loss)}</p>
        </div>
      </div>

      {/* Live Position (if active) */}
      {(trade.status === "ACTIVE" || trade.status === "OPEN") && (
        <div className="border-t border-gray-800 pt-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Live Position</p>
            <button
              onClick={() => onRefresh?.(trade)}
              className="text-gray-400 hover:text-amber-400 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-xs text-gray-500">Position</p>
              <p className="font-medium mt-0.5">{trade.position_size.toFixed(4)} {baseSymbol}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Mark</p>
              <p className="font-medium mt-0.5">{trade.mark_price ? formatPrice(trade.mark_price) : '-'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Unrealized</p>
              <p className={`font-semibold mt-0.5 ${trade.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {trade.unrealized_pnl >= 0 ? '+' : ''}{formatUSD(trade.unrealized_pnl)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Realized</p>
              <p className={`font-semibold mt-0.5 ${trade.realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {trade.realized_pnl >= 0 ? '+' : ''}{formatUSD(trade.realized_pnl)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Entries */}
      {mainEntries.length > 0 && (
        <div className="border-t border-gray-800 pt-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Entries</p>
          <div className="flex flex-wrap gap-2">
            {mainEntries.map((entry) => (
              <div
                key={entry.id}
                className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 border ${
                  entry.filled
                    ? "bg-amber-500/10 border-amber-500/40 text-amber-400"
                    : "bg-gray-800 border-gray-700 text-gray-400"
                }`}
              >
                {entry.filled && <Check className="w-3 h-3" />}
                {entry.label}: {formatPrice(entry.price)} ({formatUSD(entry.size_usd)})
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rebuys */}
      {rebuys.length > 0 && (
        <div className="border-t border-gray-800 pt-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Rebuys</p>
          <div className="flex flex-wrap gap-2">
            {rebuys.map((rebuy) => (
              <div
                key={rebuy.id}
                className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 border ${
                  rebuy.filled
                    ? "bg-amber-500/10 border-amber-500/40 text-amber-400"
                    : "bg-orange-500/10 border-orange-500/30 text-orange-400"
                }`}
              >
                {rebuy.filled && <Check className="w-3 h-3" />}
                {rebuy.label}: {formatPrice(rebuy.price)} ({formatUSD(rebuy.size_usd)})
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Take Profits */}
      {trade.take_profits.length > 0 && (
        <div className="border-t border-gray-800 pt-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Take Profits</p>
          <div className="flex flex-wrap gap-2">
            {trade.take_profits.map((tp) => (
              <div
                key={tp.id}
                className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 border ${
                  tp.filled
                    ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
                    : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                }`}
              >
                {tp.filled && <Check className="w-3 h-3" />}
                {tp.level}: {formatPrice(tp.price)} ({tp.size_percent}%)
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stop Loss badge */}
      <div className="border-t border-gray-800 pt-4">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Stop Loss</p>
        <div className="inline-flex px-2.5 py-1 rounded text-xs font-medium border bg-red-500/10 border-red-500/30 text-red-400">
          SL: {formatPrice(trade.stop_loss)}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-800">
        {trade.status === "PENDING" && onStart && (
          <button
            onClick={() => onStart(trade)}
            className="flex-1 min-w-[100px] px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors"
          >
            Deploy
          </button>
        )}
        {onEdit && trade.status !== "CLOSED" && (
          <button
            onClick={() => onEdit(trade)}
            className="px-4 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg font-medium transition-colors border border-amber-500/30"
          >
            Edit
          </button>
        )}
        {onClose && (trade.status === "ACTIVE" || trade.status === "OPEN") && (
          <button
            onClick={() => onClose(trade)}
            className="flex-1 min-w-[100px] px-4 py-2 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white rounded-lg font-semibold transition-colors"
          >
            Close
          </button>
        )}
        {trade.status === "CLOSED" && (
          <span className="px-4 py-2 text-gray-500 text-sm">Trade closed</span>
        )}
      </div>
    </div>
  );
}
