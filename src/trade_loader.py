"""Trade plan JSON loader and validator"""
import json
from pathlib import Path
from typing import Union
from .models import TradePlan


class TradeLoader:
    """Loads and validates trade plans from JSON files"""

    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> TradePlan:
        """
        Load trade plan from JSON file

        Args:
            file_path: Path to JSON file

        Returns:
            Validated TradePlan object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or doesn't match schema
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Trade plan file not found: {file_path}")

        with open(file_path, 'r') as f:
            data = json.load(f)

        return TradeLoader.load_from_dict(data)

    @staticmethod
    def load_from_dict(data: dict) -> TradePlan:
        """
        Load trade plan from dictionary

        Args:
            data: Dictionary containing trade plan

        Returns:
            Validated TradePlan object
        """
        try:
            trade_plan = TradePlan(**data)
            TradeLoader.validate_trade_plan(trade_plan)
            return trade_plan
        except Exception as e:
            raise ValueError(f"Invalid trade plan: {str(e)}")

    @staticmethod
    def validate_trade_plan(plan: TradePlan):
        """
        Additional validation logic for trade plan

        Args:
            plan: TradePlan to validate

        Raises:
            ValueError: If validation fails
        """
        setup = plan.tradeSetup

        # Validate stop loss position
        if setup.direction == "LONG":
            if setup.stopLoss >= setup.entryPrice:
                raise ValueError("For LONG, stop loss must be below entry price")

            # Validate TPs are above entry
            for tp in plan.takeProfits:
                if tp.price <= setup.entryPrice:
                    raise ValueError(f"For LONG, {tp.level} price must be above entry")
        else:  # SHORT
            if setup.stopLoss <= setup.entryPrice:
                raise ValueError("For SHORT, stop loss must be above entry price")

            # Validate TPs are below entry
            for tp in plan.takeProfits:
                if tp.price >= setup.entryPrice:
                    raise ValueError(f"For SHORT, {tp.level} price must be below entry")

        # Validate total TP percentages
        total_tp_percent = sum(tp.sizePercent for tp in plan.takeProfits)
        if total_tp_percent > 100:
            raise ValueError(f"Total TP percentages exceed 100%: {total_tp_percent}%")

        # Validate total entry margin
        total_margin = sum(entry.sizeUSD for entry in plan.orderEntries)
        if abs(total_margin - setup.marginUSD) > 1:  # Allow 1 USD rounding difference
            raise ValueError(
                f"Total entry margin ({total_margin}) doesn't match marginUSD ({setup.marginUSD})"
            )
