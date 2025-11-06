"""Terminal UI using Textual"""
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Input, Log, Label
from textual.binding import Binding
from textual import on
from pathlib import Path
import asyncio
from typing import Optional
from rich.text import Text
from rich.table import Table

from .trade_loader import TradeLoader
from .bingx_client import BingXClient
from .order_manager import OrderManager
from .strategy import TradingStrategy
from .models import TradePlan, PositionState
from .config import Config


class TradeStatusWidget(Static):
    """Widget to display current trade status"""

    def __init__(self):
        super().__init__()
        self.trade_plan: Optional[TradePlan] = None
        self.position_state: Optional[PositionState] = None

    def update_trade_plan(self, plan: TradePlan):
        """Update with new trade plan"""
        self.trade_plan = plan
        self.refresh_display()

    def update_position_state(self, state: PositionState):
        """Update position state"""
        self.position_state = state
        self.refresh_display()

    def refresh_display(self):
        """Refresh the display"""
        if not self.trade_plan:
            self.update("No trade plan loaded")
            return

        setup = self.trade_plan.tradeSetup
        state = self.position_state

        # Create status table
        table = Table(title="Trade Status", show_header=True, header_style="bold magenta")
        table.add_column("Item", style="cyan")
        table.add_column("Value", style="green")

        # Trade Setup
        table.add_row("Symbol", setup.symbol)
        table.add_row("Direction", setup.direction)
        table.add_row("Margin", f"${setup.marginUSD:.2f}")
        table.add_row("Leverage", setup.leverage)
        table.add_row("Entry Price", f"{setup.entryPrice:.6f}")
        table.add_row("Stop Loss", f"{setup.stopLoss:.6f}")

        if state:
            table.add_row("", "")
            table.add_row("[bold]Position State[/bold]", "")
            table.add_row("Filled Entries", f"{len(state.filled_entries)}/{len(self.trade_plan.orderEntries)}")
            table.add_row("Avg Entry", f"{state.average_entry:.6f}" if state.average_entry > 0 else "N/A")
            table.add_row("Position Size", f"${state.total_size_usd:.2f}")
            table.add_row("Current SL", f"{state.current_sl_price:.6f}")
            table.add_row("In Profit", "Yes" if state.is_in_profit else "No")
            table.add_row("TPs Hit", f"{len(state.filled_tps)}/{len(self.trade_plan.takeProfits)}")

        self.update(table)


class OrderBookWidget(Static):
    """Widget to display order book (entries and TPs)"""

    def __init__(self):
        super().__init__()
        self.trade_plan: Optional[TradePlan] = None

    def update_trade_plan(self, plan: TradePlan):
        """Update with new trade plan"""
        self.trade_plan = plan
        self.refresh_display()

    def refresh_display(self):
        """Refresh the display"""
        if not self.trade_plan:
            self.update("No orders")
            return

        # Create entries table
        entries_table = Table(title="Entry Orders", show_header=True)
        entries_table.add_column("Label", style="cyan")
        entries_table.add_column("Price", style="yellow")
        entries_table.add_column("Size USD", style="green")
        entries_table.add_column("Status", style="magenta")

        for entry in self.trade_plan.orderEntries:
            status = "✓ Filled" if entry.filled else "○ Pending"
            entries_table.add_row(
                entry.label,
                f"{entry.price:.6f}",
                f"${entry.sizeUSD:.2f}",
                status
            )

        # Create TPs table
        tps_table = Table(title="Take Profits", show_header=True)
        tps_table.add_column("Level", style="cyan")
        tps_table.add_column("Price", style="yellow")
        tps_table.add_column("Size %", style="green")
        tps_table.add_column("Status", style="magenta")

        for tp in self.trade_plan.takeProfits:
            status = "✓ Hit" if tp.filled else "○ Pending"
            tps_table.add_row(
                tp.level,
                f"{tp.price:.6f}",
                f"{tp.sizePercent:.1f}%",
                status
            )

        # Combine tables
        self.update(f"{entries_table}\n\n{tps_table}")


class TradingTerminalApp(App):
    """Main Trading Terminal Application"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-rows: auto 1fr auto;
    }

    Header {
        column-span: 2;
    }

    #status_panel {
        border: solid green;
        padding: 1;
    }

    #orders_panel {
        border: solid blue;
        padding: 1;
    }

    #log_panel {
        column-span: 2;
        border: solid yellow;
        height: 15;
    }

    #controls {
        column-span: 2;
        height: auto;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }

    Input {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("l", "load_trade", "Load Trade"),
        Binding("s", "start_trade", "Start Trade"),
        Binding("c", "cancel_all", "Cancel All"),
    ]

    def __init__(self):
        super().__init__()
        self.client: Optional[BingXClient] = None
        self.order_manager: Optional[OrderManager] = None
        self.strategy: Optional[TradingStrategy] = None
        self.trade_loaded = False
        self.trade_active = False

    def compose(self) -> ComposeResult:
        """Create UI layout"""
        yield Header()

        with Vertical(id="status_panel"):
            yield Label("Trade Status")
            yield TradeStatusWidget()

        with Vertical(id="orders_panel"):
            yield Label("Orders")
            yield OrderBookWidget()

        with Vertical(id="log_panel"):
            yield Label("Activity Log")
            yield Log(id="activity_log")

        with Horizontal(id="controls"):
            yield Input(placeholder="JSON file path", id="file_input")
            yield Button("Load Trade", id="load_btn", variant="primary")
            yield Button("Start Trade", id="start_btn", variant="success", disabled=True)
            yield Button("Cancel All", id="cancel_btn", variant="error", disabled=True)
            yield Button("Close Position", id="close_btn", variant="error", disabled=True)

        yield Footer()

    async def on_mount(self):
        """Initialize app on mount"""
        try:
            Config.validate()

            # Initialize BingX client
            self.log_message("Initializing BingX client...")
            self.client = BingXClient(
                Config.BINGX_API_KEY,
                Config.BINGX_API_SECRET,
                Config.TESTNET
            )
            await self.client.initialize()

            self.order_manager = OrderManager(self.client)
            self.strategy = TradingStrategy(self.order_manager)

            mode = "TESTNET" if Config.TESTNET else "LIVE"
            self.log_message(f"✓ Connected to BingX ({mode})", style="green")

        except Exception as e:
            self.log_message(f"✗ Initialization failed: {e}", style="red")

    @on(Button.Pressed, "#load_btn")
    async def action_load_trade(self):
        """Load trade plan from JSON file"""
        file_input = self.query_one("#file_input", Input)
        file_path = file_input.value.strip()

        if not file_path:
            self.log_message("Please enter a JSON file path", style="yellow")
            return

        try:
            # Expand path
            full_path = Path(file_path).expanduser()

            if not full_path.is_absolute():
                full_path = Config.TRADES_DIR / file_path

            self.log_message(f"Loading trade plan from {full_path}...")

            # Load trade plan
            trade_plan = TradeLoader.load_from_file(full_path)

            # Load into order manager
            self.order_manager.load_trade_plan(trade_plan)

            # Update UI
            status_widget = self.query_one(TradeStatusWidget)
            status_widget.update_trade_plan(trade_plan)

            orders_widget = self.query_one(OrderBookWidget)
            orders_widget.update_trade_plan(trade_plan)

            # Enable start button
            self.query_one("#start_btn", Button).disabled = False

            self.trade_loaded = True
            self.log_message(f"✓ Trade plan loaded: {trade_plan.tradeSetup.symbol} {trade_plan.tradeSetup.direction}", style="green")

        except Exception as e:
            self.log_message(f"✗ Failed to load trade plan: {e}", style="red")

    @on(Button.Pressed, "#start_btn")
    async def action_start_trade(self):
        """Start the trade"""
        if not self.trade_loaded:
            self.log_message("No trade plan loaded", style="yellow")
            return

        try:
            self.log_message("Starting trade execution...")

            # Initialize trade (set leverage, place orders)
            await self.order_manager.initialize_trade()

            # Start monitoring strategy
            asyncio.create_task(self._run_strategy())

            # Update UI
            self.query_one("#start_btn", Button).disabled = True
            self.query_one("#cancel_btn", Button).disabled = False
            self.query_one("#close_btn", Button).disabled = False

            self.trade_active = True
            self.log_message("✓ Trade started - monitoring position", style="green")

            # Start UI refresh loop
            asyncio.create_task(self._refresh_ui_loop())

        except Exception as e:
            self.log_message(f"✗ Failed to start trade: {e}", style="red")

    async def _run_strategy(self):
        """Run the trading strategy"""
        try:
            await self.strategy.start_monitoring()
        except Exception as e:
            self.log_message(f"✗ Strategy error: {e}", style="red")

    async def _refresh_ui_loop(self):
        """Refresh UI widgets periodically"""
        while self.trade_active:
            try:
                # Update status widget
                status_widget = self.query_one(TradeStatusWidget)
                status_widget.update_position_state(self.order_manager.position_state)

                # Update orders widget
                orders_widget = self.query_one(OrderBookWidget)
                orders_widget.refresh_display()

                await asyncio.sleep(1)

            except Exception as e:
                self.log_message(f"UI refresh error: {e}", style="red")
                await asyncio.sleep(5)

    @on(Button.Pressed, "#cancel_btn")
    async def action_cancel_all(self):
        """Cancel all orders"""
        try:
            self.log_message("Cancelling all orders...")
            await self.order_manager.cancel_all_orders()
            self.log_message("✓ All orders cancelled", style="green")
        except Exception as e:
            self.log_message(f"✗ Failed to cancel orders: {e}", style="red")

    @on(Button.Pressed, "#close_btn")
    async def action_close_position(self):
        """Close the entire position"""
        try:
            self.log_message("Closing position...")
            await self.order_manager.close_entire_position()
            self.strategy.stop_monitoring()
            self.trade_active = False
            self.log_message("✓ Position closed", style="green")
        except Exception as e:
            self.log_message(f"✗ Failed to close position: {e}", style="red")

    def log_message(self, message: str, style: str = "white"):
        """Log a message to the activity log"""
        log_widget = self.query_one("#activity_log", Log)
        text = Text(message, style=style)
        log_widget.write(text)
