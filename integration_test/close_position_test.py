"""
Module: Position Closing Tests

This module contains integration tests for closing user positions within the webapp.

Key Components:
- **PositionDBConnector**: Manages database operations for positions.

Test Class:
- **PositionCloseTest**: Validates position workflows:
  1. Creating and verifying positions.
  2. Updating position statuses.
  3. Closing positions and validating the final status and attributes.
"""

from datetime import datetime
from typing import Any, Dict

import pytest
from web_app.contract_tools.mixins.dashboard import DashboardMixin
from web_app.db.crud import PositionDBConnector

position_db = PositionDBConnector()


class PositionCloseTest:
    """
    Integration test for closing and managing positions.

    Steps:
    1. Create a position using `PositionDBConnector`.
    2. Verify the created position's attributes.
    3. Update position status to 'opened'.
    4. Close the position using `PositionDBConnector`.
    5. Validate the position's final status and attributes.
    """

    form_data_1: Dict[str, Any] = {
        "wallet_id": "0x011F0c180b9EbB2B3F9601c41d65AcA110E48aec0292c778f41Ae286C78Cc374",
        "token_symbol": "STRK",
        "amount": "2",
        "multiplier": 1,
    }

    form_data_2: Dict[str, Any] = {
        "wallet_id": "0xTestWalletETH",
        "token_symbol": "ETH",
        "amount": "5",
        "multiplier": 1,
    }

    form_data_3: Dict[str, Any] = {
        "wallet_id": "0xTestWalletUSDC",
        "token_symbol": "USDC",
        "amount": "1",
        "multiplier": 1,
    }

    @pytest.mark.parametrize("form_data", [form_data_1, form_data_2, form_data_3])
    def test_close_position(self, form_data: Dict[str, Any]) -> None:
        """
        Args:
        form_data (Dict[str, Any]): Position data.

        Returns:
            None
        """
        wallet_id = form_data["wallet_id"]
        token_symbol = form_data["token_symbol"]
        amount = form_data["amount"]
        multiplier = form_data["multiplier"]

        position_db.create_user(wallet_id)

        position = position_db.create_position(
            wallet_id=wallet_id,
            token_symbol=token_symbol,
            amount=amount,
            multiplier=multiplier,
        )
        assert (
            position.status == "pending"
        ), "Position status should be 'pending' upon creation"

        current_prices = DashboardMixin.get_current_prices()
        assert (
            token_symbol in current_prices
        ), f"Token {token_symbol} missing in current prices"
        position.start_price = current_prices[token_symbol]
        position.created_at = datetime.utcnow()

        position_db.open_position(position.id, current_prices)
        assert (
            position.status == "opened"
        ), "Position status should be 'opened' after updating"

        print(
            f"Position {position.id} successfully opened with status '{position.status}'."
        )

        close_result = position_db.close_position(position.id)
        assert close_result, "Close operation should succeed."

        position = position_db.get_position_by_id(position.id)
        assert (
            position.status == "closed"
        ), "Position status should be 'closed' after close operation"
        assert (
            position.closed_at is not None
        ), "Position should have a closed_at timestamp."
        assert position.end_price is not None, "Position should have an end_price."
        assert position.end_price >= 0, "End price should be a non-negative value."

        print(
            f"Position {position.id} successfully closed with end price {position.end_price} "
            f"and closed at {position.closed_at}."
        )

        position_db.delete_position(position)
        position_db.delete_user_by_wallet_id(wallet_id)
