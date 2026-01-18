"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Trade, TradeEvent, TradeEventType, TradeStatus } from "@/types";
import {
  Shield,
  CircleCheck,
  Clock,
  ArrowRightLeft,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Target,
  XCircle,
} from "lucide-react";
import Link from "next/link";

interface ActivityItem {
  id: number;
  tradeId: number;
  symbol: string;
  direction: string;
  eventType: string;
  eventData?: Record<string, unknown>;
  createdAt: string;
  isCompleted: boolean;
}

// Event type configuration
const EVENT_CONFIG: Record<
  string,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    isCompleted: boolean;
  }
> = {
  [TradeEventType.TRADE_CREATED]: {
    label: "Created",
    icon: CircleCheck,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.TRADE_STARTED]: {
    label: "Deployed",
    icon: CircleCheck,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.ORDER_PLACED]: {
    label: "Placing",
    icon: Clock,
    color: "amber",
    isCompleted: false,
  },
  [TradeEventType.ORDER_FILLED]: {
    label: "Filled",
    icon: CircleCheck,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.ORDER_CANCELLED]: {
    label: "Cancelled",
    icon: XCircle,
    color: "gray",
    isCompleted: true,
  },
  [TradeEventType.SL_MOVED]: {
    label: "SL Moved",
    icon: Shield,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.TP_HIT]: {
    label: "TP Hit",
    icon: Target,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.POSITION_OPENED]: {
    label: "Position Opened",
    icon: TrendingUp,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.POSITION_CLOSED]: {
    label: "Position Closed",
    icon: ArrowRightLeft,
    color: "amber",
    isCompleted: false,
  },
  [TradeEventType.TRADE_CLOSED]: {
    label: "Closed",
    icon: CircleCheck,
    color: "emerald",
    isCompleted: true,
  },
  [TradeEventType.ERROR]: {
    label: "Error",
    icon: AlertCircle,
    color: "red",
    isCompleted: true,
  },
};

const DEFAULT_CONFIG = {
  label: "Event",
  icon: CircleCheck,
  color: "gray",
  isCompleted: true,
};

interface ActivityFeedProps {
  maxItems?: number;
  className?: string;
}

export default function ActivityFeed({ maxItems = 10, className = "" }: ActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        // Fetch all trades
        const trades = await api.getTrades();

        // Collect all events from all trades
        const allActivities: ActivityItem[] = [];

        for (const trade of trades) {
          try {
            const events = await api.getTradeEvents(trade.id);
            events.forEach((event) => {
              const config = EVENT_CONFIG[event.event_type] || DEFAULT_CONFIG;
              allActivities.push({
                id: event.id,
                tradeId: trade.id,
                symbol: trade.symbol
                  .replace("/USDT:USDT", "")
                  .replace("USDT", "")
                  .replace("/", "")
                  .toUpperCase(),
                direction: trade.direction,
                eventType: event.event_type,
                eventData: event.event_data ? JSON.parse(event.event_data) : undefined,
                createdAt: event.created_at,
                isCompleted: config.isCompleted,
              });
            });
          } catch {
            // Skip if no events for this trade
          }
        }

        // Sort by date descending and take top N
        allActivities.sort(
          (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );

        setActivities(allActivities.slice(0, maxItems));
      } catch (error) {
        console.error("Failed to fetch activities:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();

    // Refresh every 30 seconds
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
  }, [maxItems]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className={`space-y-2 ${className}`}>
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="bg-gray-800/30 border border-gray-700/30 rounded p-3 animate-pulse"
          >
            <div className="h-4 bg-gray-700 rounded w-3/4" />
          </div>
        ))}
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <p className="text-sm">No recent activity</p>
        <p className="text-xs mt-1">Trade events will appear here</p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {activities.map((activity) => {
        const config = EVENT_CONFIG[activity.eventType] || DEFAULT_CONFIG;
        const Icon = config.icon;
        const colorClasses = {
          emerald: {
            icon: "text-emerald-400",
            label: "text-emerald-400",
            bg: "bg-gray-700/50",
          },
          amber: {
            icon: "text-amber-400",
            label: "text-amber-400",
            bg: "bg-gray-700/50",
          },
          red: {
            icon: "text-red-400",
            label: "text-red-400",
            bg: "bg-gray-700/50",
          },
          gray: {
            icon: "text-gray-400",
            label: "text-gray-400",
            bg: "bg-gray-700/50",
          },
        }[config.color] || {
          icon: "text-gray-400",
          label: "text-gray-400",
          bg: "bg-gray-700/50",
        };

        const isClickable = activity.isCompleted;

        const content = (
          <div
            className={`flex items-start gap-3 p-2.5 sm:p-3 transition-all ${
              isClickable ? "cursor-pointer hover:bg-gray-800/50" : ""
            }`}
          >
            {/* Icon */}
            <div className={`p-1.5 rounded ${colorClasses.bg} flex-shrink-0 mt-0.5`}>
              <Icon className={`w-3.5 h-3.5 ${colorClasses.icon}`} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs font-medium ${colorClasses.label}`}>
                  {config.label}
                </span>
                <span className="text-xs font-mono text-gray-300 hover:text-amber-400">
                  {activity.symbol}
                </span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                    activity.direction === "LONG"
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "bg-red-500/10 text-red-400"
                  }`}
                >
                  {activity.direction}
                </span>
              </div>
              {isClickable && (
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] text-gray-600">click for details</span>
                </div>
              )}
            </div>

            {/* Date */}
            <span className="text-[10px] text-gray-600 flex-shrink-0">
              {formatDate(activity.createdAt)}
            </span>
          </div>
        );

        return (
          <div
            key={activity.id}
            className="bg-gray-800/30 border border-gray-700/30 rounded overflow-hidden"
          >
            {isClickable ? (
              <Link href={`/trades?id=${activity.tradeId}`}>{content}</Link>
            ) : (
              content
            )}
          </div>
        );
      })}
    </div>
  );
}
