"use client";

import { useState } from "react";
import { Upload, X, FileJson, BookOpen, ChevronDown, ChevronUp } from "lucide-react";
import { api } from "@/lib/api";
import { TradeDirection } from "@/types";

interface ImportTradeModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const SETUP_TYPES = [
  "Breakout",
  "Support Bounce",
  "Resistance Rejection",
  "Trend Continuation",
  "Reversal",
  "Range Trade",
  "News/Event",
  "Other"
];

export default function ImportTradeModal({ onClose, onSuccess }: ImportTradeModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jsonContent, setJsonContent] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showJournal, setShowJournal] = useState(true);

  // Journal fields
  const [theory, setTheory] = useState("");
  const [setupType, setSetupType] = useState("");
  const [confidenceLevel, setConfidenceLevel] = useState(3);
  const [preTradeNotes, setPreTradeNotes] = useState("");
  const [tags, setTags] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        setJsonContent(event.target?.result as string);
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jsonContent) {
      setError("Please select a JSON file");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Parse JSON
      const tradeData = JSON.parse(jsonContent);

      // Validate required fields
      if (!tradeData.tradeSetup || !tradeData.orderEntries || !tradeData.takeProfits) {
        throw new Error("Invalid trade JSON format");
      }

      // Parse tags from comma-separated string
      const parsedTags = tags
        .split(",")
        .map(t => t.trim())
        .filter(t => t.length > 0);

      // Transform to API format
      const trade = {
        symbol: tradeData.tradeSetup.symbol,
        direction: tradeData.tradeSetup.direction as TradeDirection,
        margin_usd: tradeData.tradeSetup.marginUSD,
        leverage: tradeData.tradeSetup.leverage,
        entry_price: tradeData.tradeSetup.entryPrice,
        average_price: tradeData.tradeSetup.averagePrice,
        stop_loss: tradeData.tradeSetup.stopLoss,
        max_loss_percent: tradeData.tradeSetup.maxLossPercent,
        notes: tradeData.notes || null,
        // Journal fields
        theory: theory.trim() || undefined,
        setup_type: setupType || undefined,
        confidence_level: confidenceLevel,
        pre_trade_notes: preTradeNotes.trim() || undefined,
        tags: parsedTags.length > 0 ? parsedTags : undefined,
        entries: tradeData.orderEntries.map((entry: any) => ({
          label: entry.label,
          price: entry.price,
          size_usd: entry.sizeUSD,
          average_after_fill: entry.average,
        })),
        take_profits: tradeData.takeProfits.map((tp: any) => ({
          level: tp.level,
          price: tp.price,
          size_percent: tp.sizePercent,
        })),
      };

      // Create trade
      await api.createTrade(trade);

      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to import trade");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#161b22] border border-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <FileJson className="h-6 w-6 text-teal-400" />
            <h2 className="text-2xl font-bold">Import Trade</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
              {error}
            </div>
          )}

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select JSON Trade File
            </label>
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-teal-500/50 transition-colors">
              <input
                type="file"
                accept=".json"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center gap-3"
              >
                <Upload className="h-12 w-12 text-gray-500" />
                {file ? (
                  <div>
                    <p className="text-teal-400 font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500 mt-1">Click to change file</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-400">Click to upload or drag and drop</p>
                    <p className="text-sm text-gray-500 mt-1">JSON trade plan file</p>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Preview */}
          {jsonContent && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Preview
              </label>
              <div className="bg-[#0d1117] border border-gray-700 rounded-lg p-4 max-h-48 overflow-y-auto">
                <pre className="text-xs text-gray-400 font-mono whitespace-pre-wrap">
                  {jsonContent}
                </pre>
              </div>
            </div>
          )}

          {/* Journal Section */}
          <div className="border border-gray-700 rounded-lg overflow-hidden">
            <button
              type="button"
              onClick={() => setShowJournal(!showJournal)}
              className="w-full flex items-center justify-between p-4 bg-[#0d1117] hover:bg-gray-800/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-purple-400" />
                <span className="font-medium">Trade Journal</span>
                <span className="text-xs text-gray-500">(Optional)</span>
              </div>
              {showJournal ? (
                <ChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </button>

            {showJournal && (
              <div className="p-4 space-y-4 border-t border-gray-700">
                {/* Theory */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Trade Theory / Reasoning
                  </label>
                  <textarea
                    value={theory}
                    onChange={(e) => setTheory(e.target.value)}
                    placeholder="Why are you taking this trade? What's your thesis?"
                    rows={3}
                    className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition-colors resize-none"
                  />
                </div>

                {/* Setup Type and Confidence */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Setup Type
                    </label>
                    <select
                      value={setupType}
                      onChange={(e) => setSetupType(e.target.value)}
                      className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition-colors"
                    >
                      <option value="">Select setup...</option>
                      {SETUP_TYPES.map((type) => (
                        <option key={type} value={type.toLowerCase().replace(/ /g, "_")}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Confidence Level
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={confidenceLevel}
                        onChange={(e) => setConfidenceLevel(parseInt(e.target.value))}
                        className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                      />
                      <span className="text-lg font-bold text-purple-400 w-8 text-center">
                        {confidenceLevel}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Low</span>
                      <span>High</span>
                    </div>
                  </div>
                </div>

                {/* Pre-trade Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Pre-Trade Notes
                  </label>
                  <textarea
                    value={preTradeNotes}
                    onChange={(e) => setPreTradeNotes(e.target.value)}
                    placeholder="Any additional notes, market context, or observations..."
                    rows={2}
                    className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition-colors resize-none"
                  />
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Tags
                  </label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="e.g., bitcoin, altseason, high-volume (comma-separated)"
                    className="w-full px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={!jsonContent || loading}
              className="flex-1 px-4 py-3 bg-teal-500 hover:bg-teal-600 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-medium transition-colors"
            >
              {loading ? "Importing..." : "Import Trade"}
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
