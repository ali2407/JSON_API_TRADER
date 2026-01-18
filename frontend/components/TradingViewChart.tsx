"use client";

import { useEffect, useRef, memo, useState } from "react";

interface TradingViewChartProps {
  symbol?: string;
  interval?: string;
  theme?: "dark" | "light";
  height?: number;
  autosize?: boolean;
}

function TradingViewChart({
  symbol = "BINANCE:BTCUSDT",
  interval = "60",
  theme = "dark",
  height = 500,
  autosize = true,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  // Only render on client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient || !containerRef.current) return;

    // Clear any existing widget
    containerRef.current.innerHTML = "";

    // Create widget container
    const widgetContainer = document.createElement("div");
    widgetContainer.className = "tradingview-widget-container";
    widgetContainer.style.height = "100%";
    widgetContainer.style.width = "100%";

    const widgetDiv = document.createElement("div");
    widgetDiv.className = "tradingview-widget-container__widget";
    widgetDiv.style.height = autosize ? "100%" : `${height}px`;
    widgetDiv.style.width = "100%";

    widgetContainer.appendChild(widgetDiv);
    containerRef.current.appendChild(widgetContainer);

    // Create and load the script
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      width: "100%",
      height: "100%",
      symbol: symbol,
      interval: interval,
      timezone: "Etc/UTC",
      theme: theme,
      style: "1",
      locale: "en",
      toolbar_bg: "#161b22",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      hide_side_toolbar: false,
      allow_symbol_change: true,
      save_image: true,
      calendar: false,
      hide_volume: false,
      support_host: "https://www.tradingview.com",
      backgroundColor: theme === "dark" ? "rgba(22, 27, 34, 1)" : "rgba(255, 255, 255, 1)",
      gridColor: theme === "dark" ? "rgba(66, 66, 66, 0.3)" : "rgba(200, 200, 200, 0.3)",
      withdateranges: true,
      details: true,
      hotlist: true,
    });

    widgetContainer.appendChild(script);

    // Cleanup
    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [isClient, symbol, interval, theme, height, autosize]);

  if (!isClient) {
    return (
      <div
        style={{
          height: autosize ? "100%" : `${height}px`,
          width: "100%",
          minHeight: "400px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#161b22",
        }}
      >
        <span style={{ color: "#6b7280" }}>Loading chart...</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{
        height: autosize ? "100%" : `${height}px`,
        width: "100%",
        minHeight: "400px",
      }}
    />
  );
}

export default memo(TradingViewChart);
