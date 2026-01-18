"use client";

import { useState } from "react";
import { Key, X, Eye, EyeOff, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface AddAPIKeyModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const EXCHANGES = [
  { value: "bingx", label: "BingX" },
  { value: "btcc", label: "BTCC" },
];

export default function AddAPIKeyModal({ onClose, onSuccess }: AddAPIKeyModalProps) {
  const [name, setName] = useState("");
  const [exchange, setExchange] = useState("bingx");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  // BTCC-specific fields
  const [btccUsername, setBtccUsername] = useState("");
  const [btccPassword, setBtccPassword] = useState("");
  const [showBtccPassword, setShowBtccPassword] = useState(false);

  const [testnet, setTestnet] = useState(false);
  const [isDefault, setIsDefault] = useState(true);
  const [notes, setNotes] = useState("");
  const [showSecret, setShowSecret] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validated, setValidated] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    message: string;
    balance: number | null;
  } | null>(null);

  const isBtcc = exchange === "btcc";

  const handleValidate = async () => {
    if (!apiKey.trim()) {
      setError("Please enter the API key");
      return;
    }
    if (!apiSecret.trim()) {
      setError("Please enter the API secret");
      return;
    }
    // BTCC requires username and password
    if (isBtcc) {
      if (!btccUsername.trim()) {
        setError("BTCC requires your account email or phone number");
        return;
      }
      if (!btccPassword.trim()) {
        setError("BTCC requires your account password");
        return;
      }
    }

    try {
      setValidating(true);
      setError(null);
      setValidationResult(null);

      const result = await api.validateAPIKey({
        api_key: apiKey.trim(),
        api_secret: apiSecret.trim(),
        testnet,
        exchange,
        btcc_username: isBtcc ? btccUsername.trim() : undefined,
        btcc_password: isBtcc ? btccPassword.trim() : undefined,
      });

      setValidationResult({
        valid: result.valid,
        message: result.message,
        balance: result.balance,
      });
      setValidated(result.valid);

      if (!result.valid) {
        setError(result.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to validate API key");
      setValidated(false);
    } finally {
      setValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError("Please enter a name for this API key");
      return;
    }
    if (!validated) {
      setError("Please validate the API key before adding");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await api.createAPIKey({
        name: name.trim(),
        exchange,
        api_key: apiKey.trim(),
        api_secret: apiSecret.trim(),
        btcc_username: isBtcc ? btccUsername.trim() : undefined,
        btcc_password: isBtcc ? btccPassword.trim() : undefined,
        testnet,
        is_active: true,
        is_default: isDefault,
        notes: notes.trim() || undefined,
      });

      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add API key");
    } finally {
      setLoading(false);
    }
  };

  // Reset validation when credentials change
  const handleApiKeyChange = (value: string) => {
    setApiKey(value);
    setValidated(false);
    setValidationResult(null);
  };

  const handleApiSecretChange = (value: string) => {
    setApiSecret(value);
    setValidated(false);
    setValidationResult(null);
  };

  const handleTestnetChange = (value: boolean) => {
    setTestnet(value);
    setValidated(false);
    setValidationResult(null);
  };

  const handleExchangeChange = (value: string) => {
    setExchange(value);
    setValidated(false);
    setValidationResult(null);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#161b22] border border-gray-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <Key className="h-6 w-6 text-teal-400" />
            <h2 className="text-2xl font-bold">Add API Key</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
              {error}
            </div>
          )}

          {/* Validation Success */}
          {validationResult?.valid && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">Connection Verified</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                Account Type: <span className="text-white">{testnet ? "Testnet" : "Live"}</span>
                {validationResult.balance !== null && (
                  <>
                    <br />
                    USDT Balance: <span className="text-green-400">${validationResult.balance.toFixed(2)}</span>
                  </>
                )}
              </p>
            </div>
          )}

          {/* Exchange Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Exchange
            </label>
            <div className="grid grid-cols-2 gap-2">
              {EXCHANGES.map((ex) => (
                <button
                  key={ex.value}
                  type="button"
                  onClick={() => handleExchangeChange(ex.value)}
                  className={`px-4 py-3 rounded-lg font-medium transition-colors border ${
                    exchange === ex.value
                      ? "bg-teal-500/20 border-teal-500 text-teal-400"
                      : "bg-[#0d1117] border-gray-700 text-gray-400 hover:border-gray-600"
                  }`}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Account Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Main Trading Account"
              className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none transition-colors"
            />
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Key
            </label>
            <div className="relative">
              <input
                type="text"
                value={apiKey}
                onChange={(e) => handleApiKeyChange(e.target.value)}
                placeholder={`Enter your ${EXCHANGES.find(e => e.value === exchange)?.label} API key`}
                className={`w-full px-4 py-3 pr-10 bg-[#0d1117] border rounded-lg focus:outline-none transition-colors font-mono text-sm ${
                  validated ? "border-green-500" : "border-gray-700 focus:border-teal-500"
                }`}
              />
              {validated && (
                <CheckCircle className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-green-500" />
              )}
            </div>
          </div>

          {/* API Secret */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Secret
            </label>
            <div className="relative">
              <input
                type={showSecret ? "text" : "password"}
                value={apiSecret}
                onChange={(e) => handleApiSecretChange(e.target.value)}
                placeholder={`Enter your ${EXCHANGES.find(e => e.value === exchange)?.label} API secret`}
                className={`w-full px-4 py-3 pr-20 bg-[#0d1117] border rounded-lg focus:outline-none transition-colors font-mono text-sm ${
                  validated ? "border-green-500" : "border-gray-700 focus:border-teal-500"
                }`}
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
                {validated && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                <button
                  type="button"
                  onClick={() => setShowSecret(!showSecret)}
                  className="p-1 hover:bg-gray-700 rounded transition-colors"
                >
                  {showSecret ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* BTCC-specific: Username and Password */}
          {isBtcc && (
            <>
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 text-sm text-amber-400">
                BTCC requires your account login credentials (email/phone and password) in addition to API keys.
              </div>

              {/* BTCC Username */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  BTCC Email or Phone
                </label>
                <input
                  type="text"
                  value={btccUsername}
                  onChange={(e) => {
                    setBtccUsername(e.target.value);
                    setValidated(false);
                    setValidationResult(null);
                  }}
                  placeholder="Enter your BTCC account email or phone"
                  className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none transition-colors"
                />
              </div>

              {/* BTCC Password */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  BTCC Password
                </label>
                <div className="relative">
                  <input
                    type={showBtccPassword ? "text" : "password"}
                    value={btccPassword}
                    onChange={(e) => {
                      setBtccPassword(e.target.value);
                      setValidated(false);
                      setValidationResult(null);
                    }}
                    placeholder="Enter your BTCC account password"
                    className="w-full px-4 py-3 pr-12 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowBtccPassword(!showBtccPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-700 rounded transition-colors"
                  >
                    {showBtccPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Options */}
          <div className="flex flex-col gap-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={testnet}
                onChange={(e) => handleTestnetChange(e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-[#0d1117] text-teal-500 focus:ring-teal-500 focus:ring-offset-0"
              />
              <span className="text-sm text-gray-300">Testnet Mode</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isDefault}
                onChange={(e) => setIsDefault(e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-[#0d1117] text-teal-500 focus:ring-teal-500 focus:ring-offset-0"
              />
              <span className="text-sm text-gray-300">Set as default account</span>
            </label>
          </div>

          {/* Test Connection Button */}
          <div>
            <button
              type="button"
              onClick={handleValidate}
              disabled={validating || !apiKey.trim() || !apiSecret.trim()}
              className={`w-full px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                validated
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 disabled:bg-gray-700/50 disabled:text-gray-500 disabled:border-gray-700"
              }`}
            >
              {validating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Testing Connection...
                </>
              ) : validated ? (
                <>
                  <CheckCircle className="h-5 w-5" />
                  Connection Verified
                </>
              ) : (
                "Test Connection"
              )}
            </button>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes about this account..."
              rows={2}
              className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-teal-500 focus:outline-none transition-colors resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading || !validated}
              className="flex-1 px-4 py-3 bg-teal-500 hover:bg-teal-600 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-medium transition-colors"
            >
              {loading ? "Adding..." : "Add API Key"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
