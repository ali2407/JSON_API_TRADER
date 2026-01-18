"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  LineStyle,
  ColorType,
  Time,
  CandlestickSeries,
  IPriceLine,
} from "lightweight-charts";
import { api } from "@/lib/api";
import { Trade, OrderEntry, TakeProfit } from "@/types";

interface OrderLevel {
  price: number;
  label: string;
  type: "entry" | "tp" | "sl" | "rebuy";
  filled?: boolean;
}

interface LightweightChartProps {
  symbol: string;
  interval?: string;
  trade?: Trade | null;
  height?: number;
  className?: string;
}

// Order line colors from reference terminal
const LINE_COLORS = {
  entry: "#3b82f6",    // blue-500
  tp: "#10b981",       // emerald-500
  sl: "#ef4444",       // red-500
  rebuy: "#f97316",    // orange-500
};

const LINE_STYLES = {
  entry: LineStyle.Dashed,
  tp: LineStyle.Solid,
  sl: LineStyle.Solid,
  rebuy: LineStyle.Dotted,
};

// Calculate decimal precision based on price magnitude
const getPrecision = (price: number): number => {
  if (price >= 1000) return 2;      // BTC: $93,000.00
  if (price >= 100) return 3;       // ETH: $3,400.000
  if (price >= 1) return 4;         // XRP: $2.1100
  if (price >= 0.01) return 5;      // DOGE: $0.40000
  return 6;                          // SHIB: $0.000025
};

export default function LightweightChart({
  symbol,
  interval = "1h",
  trade,
  height,
  className = "",
}: LightweightChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<CandlestickSeries> | null>(null);
  const priceLinesRef = useRef<IPriceLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [chartReady, setChartReady] = useState(false);
  const symbolRef = useRef<string>(symbol); // Track current symbol to detect changes

  // Extract order levels from trade
  const getOrderLevels = useCallback((): OrderLevel[] => {
    if (!trade) return [];

    const levels: OrderLevel[] = [];

    // Add entry orders
    trade.entries.forEach((entry: OrderEntry) => {
      const isRebuy = entry.label.toLowerCase().startsWith("rb") ||
                      entry.label.toLowerCase().startsWith("rebuy");
      levels.push({
        price: entry.price,
        label: entry.label,
        type: isRebuy ? "rebuy" : "entry",
        filled: entry.filled,
      });
    });

    // Add take profits
    trade.take_profits.forEach((tp: TakeProfit) => {
      levels.push({
        price: tp.price,
        label: tp.level,
        type: "tp",
        filled: tp.filled,
      });
    });

    // Add stop loss
    if (trade.stop_loss) {
      levels.push({
        price: trade.stop_loss,
        label: "SL",
        type: "sl",
      });
    }

    return levels;
  }, [trade]);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Get container dimensions - use parent height if available
    const container = chartContainerRef.current;
    const containerWidth = container.clientWidth || 800;
    const containerHeight = height || container.parentElement?.clientHeight || container.clientHeight || 600;

    const chart = createChart(container, {
      width: containerWidth,
      height: containerHeight,
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "#0d1117" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "#1e2530" },
        horzLines: { color: "#1e2530" },
      },
      rightPriceScale: {
        borderColor: "#1e2530",
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: "#1e2530",
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        vertLine: {
          color: "#4b5563",
          labelBackgroundColor: "#374151",
        },
        horzLine: {
          color: "#4b5563",
          labelBackgroundColor: "#374151",
        },
      },
    });

    // Create candlestick series (v5 API)
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#10b981",
      downColor: "#ef4444",
      borderUpColor: "#10b981",
      borderDownColor: "#ef4444",
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444",
    });

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;
    setChartReady(true);

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: height || chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => {
      setChartReady(false);
      window.removeEventListener("resize", handleResize);
      priceLinesRef.current = [];
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [height]); // Only recreate chart when height changes, not on symbol/interval change

  // Fetch and update data
  useEffect(() => {
    // Check if symbol changed - clear old data immediately
    const symbolChanged = symbolRef.current !== symbol;
    if (symbolChanged) {
      symbolRef.current = symbol;
      // Clear old data and price lines immediately when symbol changes
      if (seriesRef.current) {
        seriesRef.current.setData([]);
        // Clear price lines
        priceLinesRef.current.forEach((line) => {
          try {
            seriesRef.current?.removePriceLine(line);
          } catch {
            // Line may already be removed
          }
        });
        priceLinesRef.current = [];
      }
      setCurrentPrice(null);
    }

    let isFirstLoad = true;

    const fetchData = async () => {
      if (!chartReady || !seriesRef.current) return;

      // Only show loading on first load, not on refreshes
      if (isFirstLoad) {
        setLoading(true);
      }
      setError(null);

      try {
        // Get base symbol (e.g., "BTC" from "BTCUSDT" or "BTC/USDT:USDT")
        const baseSymbol = symbol
          .replace("/USDT:USDT", "")
          .replace("USDT", "")
          .replace("/", "")
          .toUpperCase();

        const data = await api.getKlines(baseSymbol, interval, 500);

        // Check if symbol still matches (user may have switched during fetch)
        if (symbolRef.current !== symbol) return;

        // Convert to chart format
        const candles: CandlestickData<Time>[] = data.candles.map((c) => ({
          time: c.time as Time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        }));

        seriesRef.current.setData(candles);

        // Set current price and apply dynamic precision
        if (candles.length > 0) {
          const lastPrice = candles[candles.length - 1].close;
          setCurrentPrice(lastPrice);

          // Apply precision based on price magnitude
          const precision = getPrecision(lastPrice);
          seriesRef.current.applyOptions({
            priceFormat: {
              type: 'price',
              precision: precision,
              minMove: 1 / Math.pow(10, precision),
            },
          });
        }

        // Fit content on first load
        if (chartRef.current && isFirstLoad) {
          chartRef.current.timeScale().fitContent();
        }

        setLastUpdate(new Date());
        isFirstLoad = false;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load chart data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Fast polling every 2 seconds for near-live updates
    const refreshInterval = setInterval(fetchData, 2000);
    return () => clearInterval(refreshInterval);
  }, [symbol, interval, chartReady]);

  // Add order lines when trade changes - separate function to avoid duplicates
  const addOrderLines = useCallback(() => {
    if (!seriesRef.current) return;

    const series = seriesRef.current;

    // Remove existing price lines first
    priceLinesRef.current.forEach((line) => {
      try {
        series.removePriceLine(line);
      } catch {
        // Line may already be removed
      }
    });
    priceLinesRef.current = [];

    // Add new price lines for order levels
    const levels = getOrderLevels();

    levels.forEach((level) => {
      const lineColor = LINE_COLORS[level.type];
      const lineStyle = LINE_STYLES[level.type];

      const priceLine = series.createPriceLine({
        price: level.price,
        color: lineColor,
        lineWidth: level.type === "sl" ? 2 : 1,
        lineStyle: lineStyle,
        axisLabelVisible: true,
        title: level.filled ? `✓ ${level.label}` : level.label,
      });

      priceLinesRef.current.push(priceLine);
    });
  }, [getOrderLevels]);

  // Add order lines when trade changes or after chart loads
  useEffect(() => {
    // Only add lines when not loading (chart is ready with data)
    if (!loading && seriesRef.current) {
      addOrderLines();
    }
  }, [trade, loading, addOrderLines]);

  return (
    <div className={`relative h-full ${className}`}>
      {/* Chart container */}
      <div
        ref={chartContainerRef}
        className="w-full h-full"
      />

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0d1117]/80">
          <div className="flex items-center gap-2 text-gray-400">
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading chart...</span>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0d1117]/80">
          <div className="text-red-400 text-center">
            <p className="font-medium">Failed to load chart</p>
            <p className="text-sm text-gray-500 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Current price badge */}
      {currentPrice && !loading && (
        <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 bg-gray-800/80 rounded text-sm font-mono">
          <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-gray-400">Price: </span>
          <span className="text-white">
            ${currentPrice.toLocaleString(undefined, {
              minimumFractionDigits: getPrecision(currentPrice),
              maximumFractionDigits: getPrecision(currentPrice),
            })}
          </span>
        </div>
      )}
    </div>
  );
}
