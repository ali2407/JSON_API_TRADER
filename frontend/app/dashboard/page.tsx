"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { TradeSummary, APIKey } from "@/types";
import { TrendingUp, Activity, DollarSign, RefreshCw, Upload } from "lucide-react";
import ImportTradeModal from "@/components/ImportTradeModal";
import AddAPIKeyModal from "@/components/AddAPIKeyModal";
import ActivityFeed from "@/components/ActivityFeed";

export default function DashboardPage() {
  const [summary, setSummary] = useState<TradeSummary | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showAPIKeyModal, setShowAPIKeyModal] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [secondsAgo, setSecondsAgo] = useState<number>(0);

  const fetchSummary = async (isInitial = false) => {
    try {
      if (isInitial) setLoading(true);
      setIsRefreshing(true);
      const [data, keys] = await Promise.all([
        api.getSummary(),
        api.getAPIKeys()
      ]);
      setSummary(prev => JSON.stringify(prev) === JSON.stringify(data) ? prev : data);
      setApiKeys(prev => JSON.stringify(prev) === JSON.stringify(keys) ? prev : keys);
      setLastUpdate(new Date());
      if (error) setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load summary");
    } finally {
      if (isInitial) setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSummary(true);

    // Auto-refresh dashboard every 3 seconds
    const interval = setInterval(() => {
      fetchSummary();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Update seconds ago counter every second
  useEffect(() => {
    const timer = setInterval(() => {
      if (lastUpdate) {
        setSecondsAgo(Math.floor((Date.now() - lastUpdate.getTime()) / 1000));
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [lastUpdate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-400">Loading...</div>
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
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-400 mt-1">Overview of your trading activity</p>
        </div>
        <div className="flex items-center gap-4">
          {/* Live indicator */}
          <div className="flex items-center gap-2 text-sm">
            <span className={`h-2 w-2 rounded-full ${isRefreshing ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`}></span>
            <span className="text-gray-400">
              {lastUpdate ? `${secondsAgo}s ago` : 'Connecting...'}
            </span>
          </div>
          <button
            onClick={() => fetchSummary()}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Sync
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Trades */}
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">TOTAL TRADES</p>
              <p className="text-3xl font-bold mt-2">{summary?.total_trades || 0}</p>
              <p className="text-xs text-gray-500 mt-2">
                {summary?.pending || 0} pending · {summary?.active || 0} active · {summary?.open || 0} open
              </p>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-400" />
            </div>
          </div>
        </div>

        {/* Connected Accounts */}
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">CONNECTED ACCOUNTS</p>
              <p className="text-3xl font-bold mt-2">{apiKeys.length}</p>
              <button
                onClick={() => setShowAPIKeyModal(true)}
                className="flex items-center gap-1 text-xs text-teal-400 hover:text-teal-300 mt-2"
              >
                <span className="h-2 w-2 bg-teal-400 rounded-full"></span>
                Add an API key
              </button>
            </div>
            <div className="p-3 bg-teal-500/10 rounded-lg">
              <Activity className="h-6 w-6 text-teal-400" />
            </div>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">UNREALIZED P&L</p>
              <p className={`text-3xl font-bold mt-2 ${(summary?.total_unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${summary?.total_unrealized_pnl.toFixed(2) || '0.00'}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Realized: ${summary?.total_realized_pnl.toFixed(2) || '0.00'}
              </p>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <DollarSign className="h-6 w-6 text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Trade Status */}
      <div>
        <h2 className="text-xl font-bold mb-4">Trade Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#161b22] border border-yellow-900/30 rounded-lg p-4">
            <p className="text-yellow-600 text-sm uppercase font-medium">Pending</p>
            <p className="text-3xl font-bold mt-2">{summary?.pending || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Not started yet</p>
          </div>

          <div className="bg-[#161b22] border border-blue-900/30 rounded-lg p-4">
            <p className="text-blue-400 text-sm uppercase font-medium">Active</p>
            <p className="text-3xl font-bold mt-2">{summary?.active || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Orders placed</p>
          </div>

          <div className="bg-[#161b22] border border-teal-900/30 rounded-lg p-4">
            <p className="text-teal-400 text-sm uppercase font-medium">Open</p>
            <p className="text-3xl font-bold mt-2">{summary?.open || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Position open</p>
          </div>

          <div className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-sm uppercase font-medium">Closed</p>
            <p className="text-3xl font-bold mt-2">{summary?.closed || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Completed</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => setShowImportModal(true)}
            className="bg-[#161b22] border border-gray-800 hover:border-teal-500/50 rounded-xl p-6 text-left transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors">
                <Upload className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <p className="font-medium">Import Trade</p>
                <p className="text-sm text-gray-400">Import from JSON</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => setShowAPIKeyModal(true)}
            className="bg-[#161b22] border border-gray-800 hover:border-teal-500/50 rounded-xl p-6 text-left transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 bg-teal-500/10 rounded-lg group-hover:bg-teal-500/20 transition-colors">
                <Activity className="h-6 w-6 text-teal-400" />
              </div>
              <div>
                <p className="font-medium">Connect Account</p>
                <p className="text-sm text-gray-400">Add an API key</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5">
          <ActivityFeed maxItems={8} />
        </div>
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <ImportTradeModal
          onClose={() => setShowImportModal(false)}
          onSuccess={() => {
            fetchSummary();
            alert("Trade imported successfully!");
          }}
        />
      )}

      {/* Add API Key Modal */}
      {showAPIKeyModal && (
        <AddAPIKeyModal
          onClose={() => setShowAPIKeyModal(false)}
          onSuccess={() => {
            fetchSummary();
            alert("API key added successfully!");
          }}
        />
      )}
    </div>
  );
}
