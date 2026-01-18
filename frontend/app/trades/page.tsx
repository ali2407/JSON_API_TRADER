"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Trade, TradeStatus, APIKey } from "@/types";
import TradeCard from "@/components/TradeCard";

type FilterTab = "ALL" | TradeStatus;

const tabs: { label: string; value: FilterTab; count?: number }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending", value: TradeStatus.PENDING },
  { label: "Active", value: TradeStatus.ACTIVE },
  { label: "Open", value: TradeStatus.OPEN },
  { label: "Closed", value: TradeStatus.CLOSED },
];

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filteredTrades, setFilteredTrades] = useState<Trade[]>([]);
  const [activeTab, setActiveTab] = useState<FilterTab>("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeExchange, setActiveExchange] = useState<string>("your exchange");

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const data = await api.getTrades();
      setTrades(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load trades");
    } finally {
      setLoading(false);
    }
  };

  const fetchActiveExchange = async () => {
    try {
      const defaultKey = await api.getDefaultAPIKey();
      setActiveExchange(defaultKey.exchange.toUpperCase());
    } catch {
      // If no default key, try to get any active key
      try {
        const keys = await api.getAPIKeys(true);
        if (keys.length > 0) {
          setActiveExchange(keys[0].exchange.toUpperCase());
        }
      } catch {
        setActiveExchange("your exchange");
      }
    }
  };

  useEffect(() => {
    fetchTrades();
    fetchActiveExchange();

    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      fetchTrades();
    }, 5000);

    // Cleanup on unmount
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === "ALL") {
      setFilteredTrades(trades);
    } else {
      setFilteredTrades(trades.filter((trade) => trade.status === activeTab));
    }
  }, [trades, activeTab]);

  const getCountForStatus = (status: FilterTab): number => {
    if (status === "ALL") return trades.length;
    return trades.filter((trade) => trade.status === status).length;
  };

  const handleStartTrade = async (trade: Trade) => {
    if (confirm(`Start trade for ${trade.symbol}? This will place orders on ${activeExchange}.`)) {
      try {
        await api.startTrade(trade.id);
        fetchTrades(); // Refresh trades
        alert(`Trade started for ${trade.symbol}!`);
      } catch (err) {
        alert(err instanceof Error ? err.message : "Failed to start trade");
      }
    }
  };

  const handleCloseTrade = async (trade: Trade) => {
    if (confirm(`Close position for ${trade.symbol}?`)) {
      try {
        await api.closeTrade(trade.id);
        fetchTrades(); // Refresh trades
      } catch (err) {
        alert(err instanceof Error ? err.message : "Failed to close trade");
      }
    }
  };

  const handleRefreshTrade = async (trade: Trade) => {
    try {
      const updated = await api.getTrade(trade.id);
      setTrades((prev) =>
        prev.map((t) => (t.id === updated.id ? updated : t))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to refresh trade");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-400">Loading trades...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-400">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Trades</h1>
        <p className="text-gray-400 mt-1">Manage your trading positions</p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-3 border-b border-gray-800 pb-4">
        {tabs.map((tab) => {
          const count = getCountForStatus(tab.value);
          const isActive = activeTab === tab.value;

          return (
            <button
              key={tab.value}
              onClick={() => setActiveTab(tab.value)}
              className={`
                px-4 py-2 rounded-lg font-medium transition-colors
                ${
                  isActive
                    ? "bg-teal-500/10 text-teal-400"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
                }
              `}
            >
              {tab.label}
              <span className="ml-2 text-sm opacity-70">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Trades Grid */}
      {filteredTrades.length === 0 ? (
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-12 text-center">
          <p className="text-gray-500">No {activeTab !== "ALL" && activeTab.toLowerCase()} trades found</p>
          <p className="text-sm text-gray-600 mt-2">Import a trade plan to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredTrades.map((trade) => (
            <TradeCard
              key={trade.id}
              trade={trade}
              onStart={handleStartTrade}
              onClose={handleCloseTrade}
              onRefresh={handleRefreshTrade}
            />
          ))}
        </div>
      )}
    </div>
  );
}
