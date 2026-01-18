"use client";

import { useState } from "react";
import { Brain, Lightbulb, TrendingUp, MessageSquare, Loader2, Send, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { AnalysisResponse } from "@/types";

export default function AnalysisPage() {
  const [insights, setInsights] = useState<AnalysisResponse | null>(null);
  const [patterns, setPatterns] = useState<AnalysisResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState({
    insights: false,
    patterns: false,
    question: false,
  });
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = async () => {
    try {
      setLoading((prev) => ({ ...prev, insights: true }));
      setError(null);
      const result = await api.getInsights();
      setInsights(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get insights");
    } finally {
      setLoading((prev) => ({ ...prev, insights: false }));
    }
  };

  const fetchPatterns = async () => {
    try {
      setLoading((prev) => ({ ...prev, patterns: true }));
      setError(null);
      const result = await api.findPatterns();
      setPatterns(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to find patterns");
    } finally {
      setLoading((prev) => ({ ...prev, patterns: false }));
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    try {
      setLoading((prev) => ({ ...prev, question: true }));
      setError(null);
      const result = await api.askQuestion(question);
      setAnswer(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get answer");
    } finally {
      setLoading((prev) => ({ ...prev, question: false }));
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Brain className="h-8 w-8 text-purple-400" />
          AI Trade Analysis
        </h1>
        <p className="text-gray-400 mt-1">
          Get AI-powered insights from your trading history
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Analysis Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Insights Card */}
        <div className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Lightbulb className="h-6 w-6 text-yellow-400" />
                <h2 className="text-xl font-bold">Performance Insights</h2>
              </div>
              <button
                onClick={fetchInsights}
                disabled={loading.insights}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-lg hover:bg-purple-500/30 disabled:opacity-50 transition-colors"
              >
                {loading.insights ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Generate
              </button>
            </div>
          </div>
          <div className="p-6">
            {insights?.success ? (
              <div className="space-y-4">
                {insights.stats && (
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-[#0d1117] rounded-lg p-3">
                      <p className="text-xs text-gray-500">Total Trades</p>
                      <p className="text-xl font-bold">{insights.stats.total_trades}</p>
                    </div>
                    <div className="bg-[#0d1117] rounded-lg p-3">
                      <p className="text-xs text-gray-500">Closed</p>
                      <p className="text-xl font-bold">{insights.stats.closed_trades}</p>
                    </div>
                  </div>
                )}
                <div className="prose prose-invert prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-300 text-sm leading-relaxed">
                    {insights.insights}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Click Generate to get AI-powered insights from your trading history
              </p>
            )}
          </div>
        </div>

        {/* Pattern Recognition Card */}
        <div className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-6 w-6 text-teal-400" />
                <h2 className="text-xl font-bold">Pattern Analysis</h2>
              </div>
              <button
                onClick={fetchPatterns}
                disabled={loading.patterns}
                className="flex items-center gap-2 px-4 py-2 bg-teal-500/20 text-teal-400 border border-teal-500/30 rounded-lg hover:bg-teal-500/30 disabled:opacity-50 transition-colors"
              >
                {loading.patterns ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Analyze
              </button>
            </div>
          </div>
          <div className="p-6">
            {patterns?.success ? (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-[#0d1117] rounded-lg p-3">
                    <p className="text-xs text-gray-500">Trades</p>
                    <p className="text-xl font-bold">{patterns.trade_count}</p>
                  </div>
                  <div className="bg-[#0d1117] rounded-lg p-3">
                    <p className="text-xs text-gray-500">Win Rate</p>
                    <p className="text-xl font-bold text-green-400">{patterns.win_rate}</p>
                  </div>
                  <div className="bg-[#0d1117] rounded-lg p-3">
                    <p className="text-xs text-gray-500">Total P&L</p>
                    <p className={`text-xl font-bold ${(patterns.total_pnl || 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
                      ${patterns.total_pnl?.toFixed(2)}
                    </p>
                  </div>
                </div>
                <div className="prose prose-invert prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-300 text-sm leading-relaxed">
                    {patterns.analysis}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Click Analyze to find patterns in your winning and losing trades
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Ask AI Section */}
      <div className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <MessageSquare className="h-6 w-6 text-blue-400" />
            <h2 className="text-xl font-bold">Ask About Your Trading</h2>
          </div>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && askQuestion()}
              placeholder="e.g., What's my best performing setup type? Which symbols do I trade most profitably?"
              className="flex-1 px-4 py-3 bg-[#0d1117] border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
            />
            <button
              onClick={askQuestion}
              disabled={loading.question || !question.trim()}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              {loading.question ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
              Ask
            </button>
          </div>

          {/* Quick Questions */}
          <div className="flex flex-wrap gap-2">
            {[
              "What's my win rate?",
              "Which setup type works best for me?",
              "How often do I hit TP2?",
              "What should I improve?",
            ].map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-full text-gray-400 hover:text-white transition-colors"
              >
                {q}
              </button>
            ))}
          </div>

          {answer?.success && (
            <div className="mt-6 p-4 bg-[#0d1117] border border-gray-700 rounded-lg">
              <p className="text-sm text-gray-500 mb-2">Q: {answer.question}</p>
              <div className="prose prose-invert prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                  {answer.answer}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
        <p className="text-sm text-purple-300">
          <strong>Tip:</strong> The more trades you complete with journal entries (theory, setup type, tags),
          the more accurate and insightful the AI analysis will be. Make sure to fill out the journal
          when importing trades!
        </p>
      </div>
    </div>
  );
}
