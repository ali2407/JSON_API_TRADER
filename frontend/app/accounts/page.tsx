"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { APIKey, APIKeyCreate } from "@/types";
import { Plus, Key, Trash2, Eye, EyeOff, Check } from "lucide-react";

export default function AccountsPage() {
  const [apiKeys, setAPIKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // Form state
  const [formData, setFormData] = useState<APIKeyCreate>({
    name: "",
    exchange: "bingx",
    api_key: "",
    api_secret: "",
    testnet: true,
    is_active: true,
    is_default: false,
    notes: "",
  });
  const [showSecret, setShowSecret] = useState(false);

  const fetchAPIKeys = async () => {
    try {
      setLoading(true);
      const data = await api.getAPIKeys();
      setAPIKeys(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load API keys");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createAPIKey(formData);
      setShowAddForm(false);
      setFormData({
        name: "",
        exchange: "bingx",
        api_key: "",
        api_secret: "",
        testnet: true,
        is_active: true,
        is_default: false,
        notes: "",
      });
      fetchAPIKeys();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to add API key");
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Delete this API key?")) {
      try {
        await api.deleteAPIKey(id);
        fetchAPIKeys();
      } catch (err) {
        alert(err instanceof Error ? err.message : "Failed to delete API key");
      }
    }
  };

  const toggleDefault = async (id: number, currentDefault: boolean) => {
    try {
      await api.updateAPIKey(id, { is_default: !currentDefault });
      fetchAPIKeys();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update API key");
    }
  };

  const toggleActive = async (id: number, currentActive: boolean) => {
    try {
      await api.updateAPIKey(id, { is_active: !currentActive });
      fetchAPIKeys();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update API key");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Accounts</h1>
          <p className="text-gray-400 mt-1">Manage your exchange API keys</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-500 hover:bg-teal-600 rounded-lg font-medium transition-colors"
        >
          <Plus className="h-5 w-5" />
          Add API Key
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="bg-[#161b22] border border-gray-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-bold mb-4">Add New API Key</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My BingX Account"
                required
                className="w-full px-4 py-2 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Exchange
              </label>
              <select
                value={formData.exchange}
                onChange={(e) => setFormData({ ...formData, exchange: e.target.value })}
                className="w-full px-4 py-2 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none"
              >
                <option value="bingx">BingX</option>
                <option value="btcc">BTCC</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Key *
            </label>
            <input
              type="text"
              value={formData.api_key}
              onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              placeholder="Your API Key"
              required
              className="w-full px-4 py-2 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Secret *
            </label>
            <div className="relative">
              <input
                type={showSecret ? "text" : "password"}
                value={formData.api_secret}
                onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                placeholder="Your API Secret"
                required
                className="w-full px-4 py-2 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none font-mono text-sm pr-12"
              />
              <button
                type="button"
                onClick={() => setShowSecret(!showSecret)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
              >
                {showSecret ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Optional notes about this account"
              rows={2}
              className="w-full px-4 py-2 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none resize-none"
            />
          </div>

          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.testnet}
                onChange={(e) => setFormData({ ...formData, testnet: e.target.checked })}
                className="w-4 h-4 rounded border-gray-700 bg-[#0d1117] text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-300">Use Testnet</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_default}
                onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                className="w-4 h-4 rounded border-gray-700 bg-[#0d1117] text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-300">Set as Default</span>
            </label>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 rounded-lg font-medium transition-colors"
            >
              Add API Key
            </button>
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* API Keys List */}
      {apiKeys.length === 0 ? (
        <div className="bg-[#161b22] border border-gray-800 rounded-xl p-12 text-center">
          <Key className="h-12 w-12 mx-auto mb-3 text-gray-600" />
          <p className="text-gray-500">No API keys added yet</p>
          <p className="text-sm text-gray-600 mt-2">Add your first API key to start trading</p>
        </div>
      ) : (
        <div className="space-y-4">
          {apiKeys.map((apiKey) => (
            <div
              key={apiKey.id}
              className="bg-[#161b22] border border-gray-800 rounded-xl p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold">{apiKey.name}</h3>
                    {apiKey.is_default && (
                      <span className="px-2 py-1 bg-teal-500/20 text-teal-400 text-xs font-medium rounded">
                        DEFAULT
                      </span>
                    )}
                    {apiKey.testnet && (
                      <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs font-medium rounded">
                        TESTNET
                      </span>
                    )}
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      apiKey.is_active
                        ? "bg-green-500/20 text-green-400"
                        : "bg-gray-500/20 text-gray-400"
                    }`}>
                      {apiKey.is_active ? "ACTIVE" : "DISABLED"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-400">Exchange</p>
                      <p className="font-medium mt-1">{apiKey.exchange.toUpperCase()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">API Key</p>
                      <p className="font-mono text-sm mt-1">{apiKey.api_key_preview}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Created</p>
                      <p className="text-sm mt-1">
                        {new Date(apiKey.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Last Used</p>
                      <p className="text-sm mt-1">
                        {apiKey.last_used_at
                          ? new Date(apiKey.last_used_at).toLocaleDateString()
                          : "Never"}
                      </p>
                    </div>
                  </div>

                  {apiKey.notes && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-400">Notes</p>
                      <p className="text-sm mt-1">{apiKey.notes}</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => toggleDefault(apiKey.id, apiKey.is_default)}
                    className={`p-2 rounded-lg transition-colors ${
                      apiKey.is_default
                        ? "bg-teal-500/20 text-teal-400"
                        : "bg-gray-800 hover:bg-gray-700 text-gray-400"
                    }`}
                    title={apiKey.is_default ? "Remove as default" : "Set as default"}
                  >
                    <Check className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(apiKey.id)}
                    className="p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
