"""AI-powered trade analysis using OpenAI"""
import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class TradeAnalyzer:
    """AI-powered trade analysis and pattern recognition"""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4o"  # Using GPT-4o for best analysis

    def _format_trade_for_analysis(self, trade: Dict) -> str:
        """Format a trade for AI analysis"""
        return f"""
Trade ID: {trade.get('trade_id', 'N/A')}
Symbol: {trade.get('symbol', 'N/A')}
Direction: {trade.get('direction', 'N/A')}
Status: {trade.get('status', 'N/A')}

Setup:
- Entry Price: ${trade.get('entry_price', 0):.4f}
- Stop Loss: ${trade.get('stop_loss', 0):.4f}
- Margin: ${trade.get('margin_usd', 0):.2f}
- Leverage: {trade.get('leverage', 'N/A')}

Results:
- Realized P&L: ${trade.get('realized_pnl', 0):.2f}
- Unrealized P&L: ${trade.get('unrealized_pnl', 0):.2f}
- Position Size: {trade.get('position_size', 0)}
- Average Entry: ${trade.get('avg_entry', 0):.4f}

Journal:
- Theory: {trade.get('theory', 'Not provided')}
- Setup Type: {trade.get('setup_type', 'Not specified')}
- Confidence Level: {trade.get('confidence_level', 'N/A')}/5
- Pre-Trade Notes: {trade.get('pre_trade_notes', 'None')}
- Post-Trade Notes: {trade.get('post_trade_notes', 'None')}
- Lessons Learned: {trade.get('lessons_learned', 'None')}
- Tags: {', '.join(trade.get('tags', [])) if trade.get('tags') else 'None'}

Take Profits Hit: {sum(1 for tp in trade.get('take_profits', []) if tp.get('filled', False))} / {len(trade.get('take_profits', []))}
Entries Filled: {sum(1 for e in trade.get('entries', []) if e.get('filled', False))} / {len(trade.get('entries', []))}
"""

    async def analyze_single_trade(self, trade: Dict) -> Dict[str, Any]:
        """Analyze a single completed trade"""
        try:
            trade_text = self._format_trade_for_analysis(trade)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert cryptocurrency trading analyst. Analyze the trade and provide:
1. A brief assessment of the trade execution
2. What went well
3. What could be improved
4. Comparison of the stated theory vs actual outcome
5. Key lessons for future trades

Be concise but insightful. Focus on actionable feedback."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this trade:\n{trade_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )

            analysis = response.choices[0].message.content

            return {
                "success": True,
                "trade_id": trade.get("trade_id"),
                "analysis": analysis,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Failed to analyze trade: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def find_patterns(self, trades: List[Dict]) -> Dict[str, Any]:
        """Find patterns across multiple trades"""
        if len(trades) < 2:
            return {
                "success": False,
                "error": "Need at least 2 trades for pattern analysis"
            }

        try:
            # Prepare trade summaries
            trade_summaries = []
            for trade in trades:
                pnl = trade.get('realized_pnl', 0) + trade.get('unrealized_pnl', 0)
                outcome = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
                tps_hit = sum(1 for tp in trade.get('take_profits', []) if tp.get('filled', False))
                total_tps = len(trade.get('take_profits', []))

                trade_summaries.append({
                    "symbol": trade.get('symbol'),
                    "direction": trade.get('direction'),
                    "setup_type": trade.get('setup_type', 'unknown'),
                    "confidence": trade.get('confidence_level'),
                    "pnl": pnl,
                    "outcome": outcome,
                    "tps_hit": f"{tps_hit}/{total_tps}",
                    "theory": trade.get('theory', '')[:100] if trade.get('theory') else 'N/A',
                    "tags": trade.get('tags', [])
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert trading pattern analyst. Analyze the trading history and identify:
1. Common patterns in winning vs losing trades
2. Which setup types perform best
3. Correlation between confidence levels and outcomes
4. TP hit rate patterns
5. Recurring themes in theories that led to wins/losses
6. Actionable recommendations for improvement

Format your response as structured insights that can help the trader improve."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze these {len(trades)} trades:\n{json.dumps(trade_summaries, indent=2)}"
                    }
                ],
                temperature=0.7,
                max_tokens=1200
            )

            analysis = response.choices[0].message.content

            # Calculate some basic stats
            wins = sum(1 for t in trade_summaries if t['outcome'] == 'WIN')
            losses = sum(1 for t in trade_summaries if t['outcome'] == 'LOSS')
            total_pnl = sum(t['pnl'] for t in trade_summaries)

            return {
                "success": True,
                "trade_count": len(trades),
                "wins": wins,
                "losses": losses,
                "win_rate": f"{(wins / len(trades) * 100):.1f}%",
                "total_pnl": total_pnl,
                "analysis": analysis,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Failed to find patterns: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_insights(self, trades: List[Dict]) -> Dict[str, Any]:
        """Generate actionable insights from trading history"""
        if not trades:
            return {
                "success": False,
                "error": "No trades to analyze"
            }

        try:
            # Calculate statistics
            total_trades = len(trades)
            closed_trades = [t for t in trades if t.get('status') == 'CLOSED']

            if not closed_trades:
                return {
                    "success": False,
                    "error": "No closed trades to analyze"
                }

            # TP hit rates
            tp_stats = {}
            for trade in closed_trades:
                for tp in trade.get('take_profits', []):
                    level = tp.get('level', 'unknown')
                    if level not in tp_stats:
                        tp_stats[level] = {'total': 0, 'hit': 0}
                    tp_stats[level]['total'] += 1
                    if tp.get('filled', False):
                        tp_stats[level]['hit'] += 1

            # Setup type performance
            setup_stats = {}
            for trade in closed_trades:
                setup = trade.get('setup_type', 'unknown') or 'unknown'
                pnl = trade.get('realized_pnl', 0)
                if setup not in setup_stats:
                    setup_stats[setup] = {'trades': 0, 'pnl': 0, 'wins': 0}
                setup_stats[setup]['trades'] += 1
                setup_stats[setup]['pnl'] += pnl
                if pnl > 0:
                    setup_stats[setup]['wins'] += 1

            # Format stats for AI
            stats_text = f"""
Trading Statistics:
- Total Trades: {total_trades}
- Closed Trades: {len(closed_trades)}

TP Hit Rates:
{json.dumps({k: f"{v['hit']}/{v['total']} ({v['hit']/v['total']*100:.1f}%)" for k, v in tp_stats.items()}, indent=2)}

Setup Type Performance:
{json.dumps({k: {'trades': v['trades'], 'total_pnl': f"${v['pnl']:.2f}", 'win_rate': f"{v['wins']/v['trades']*100:.1f}%"} for k, v in setup_stats.items()}, indent=2)}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a trading coach analyzing a trader's performance. Based on their statistics:
1. Identify their strongest and weakest areas
2. Provide 3 specific actionable recommendations
3. Highlight any concerning patterns
4. Suggest what to focus on for the next 10 trades

Be encouraging but honest. Focus on practical improvements."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze my trading performance:\n{stats_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )

            insights = response.choices[0].message.content

            return {
                "success": True,
                "stats": {
                    "total_trades": total_trades,
                    "closed_trades": len(closed_trades),
                    "tp_hit_rates": {k: f"{v['hit']}/{v['total']}" for k, v in tp_stats.items()},
                    "setup_performance": setup_stats
                },
                "insights": insights,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def ask_question(self, question: str, trades: List[Dict]) -> Dict[str, Any]:
        """Answer a specific question about trading history"""
        try:
            # Prepare context
            trade_summaries = []
            for trade in trades[:50]:  # Limit to recent 50 trades
                pnl = trade.get('realized_pnl', 0) + trade.get('unrealized_pnl', 0)
                trade_summaries.append({
                    "trade_id": trade.get('trade_id'),
                    "symbol": trade.get('symbol'),
                    "direction": trade.get('direction'),
                    "status": trade.get('status'),
                    "setup_type": trade.get('setup_type'),
                    "confidence": trade.get('confidence_level'),
                    "pnl": pnl,
                    "theory": trade.get('theory', '')[:100] if trade.get('theory') else None,
                    "tags": trade.get('tags'),
                    "created_at": trade.get('created_at')
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a helpful trading assistant with access to the trader's history.
Answer questions based on the trading data provided. Be specific and reference actual trades when possible.

Trading History ({len(trade_summaries)} trades):
{json.dumps(trade_summaries, indent=2, default=str)}"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )

            answer = response.choices[0].message.content

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "trades_analyzed": len(trade_summaries),
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_analyzer: Optional[TradeAnalyzer] = None


def get_analyzer() -> Optional[TradeAnalyzer]:
    """Get or create the trade analyzer"""
    global _analyzer
    if _analyzer is None and OPENAI_API_KEY:
        try:
            _analyzer = TradeAnalyzer()
        except Exception as e:
            logger.error(f"Failed to create analyzer: {e}")
            return None
    return _analyzer
