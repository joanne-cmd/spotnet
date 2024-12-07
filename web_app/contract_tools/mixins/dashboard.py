"""
This module contains the dashboard mixin class.
"""

import logging
from typing import Dict
from decimal import Decimal

from web_app.contract_tools.blockchain_call import StarknetClient
from web_app.contract_tools.constants import TokenParams
from web_app.contract_tools.api_request import APIRequest
from web_app.api.serializers.dashboard import DashboardResponse

logger = logging.getLogger(__name__)


CLIENT = StarknetClient()
# example of ARGENT_X_POSITION_URL
# "https://cloud.argent-api.com/v1/tokens/defi/decomposition/{wallet_id}?chain=starknet"
ARGENT_X_POSITION_URL = "https://cloud.argent-api.com/v1/tokens/defi/"

# New constant for AVNU price endpoint
AVNU_PRICE_URL = "https://starknet.impulse.avnu.fi/v1/tokens/short"


class DashboardMixin:
    """
    Mixin class for dashboard related methods.
    """

    @classmethod
    async def get_current_prices(cls) -> Dict[str, Decimal]:
        """
        Fetch current token prices from AVNU API.
        :return: Returns dictionary mapping token symbols to their current prices as Decimal.
        """
        prices = {}
        try:
            response = await APIRequest(base_url=AVNU_PRICE_URL).fetch("")
            if not response:
                return prices

            for token_data in response:
                address = token_data.get("address")
                current_price = token_data.get("currentPrice")
                try:
                    if address and current_price is not None:
                        address_with_leading_zero = TokenParams.add_underlying_address(
                            address
                        )
                        symbol = TokenParams.get_token_symbol(address_with_leading_zero)
                        if symbol:
                            # Convert to Decimal for precise calculations
                            prices[symbol] = Decimal(str(current_price))
                except (AttributeError, TypeError, ValueError) as e:
                    logger.debug(f"Error parsing price for {address}: {str(e)}")

            return prices
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return prices

    @classmethod
    async def get_wallet_balances(cls, holder_address: str) -> Dict[str, str]:
        """
        Get the wallet balances for the given holder address.
        :param holder_address: holder address
        :return: Returns the wallet balances for the given holder address.
        """
        wallet_balances = {}

        for token in TokenParams.tokens():
            try:
                balance = await CLIENT.get_balance(
                    token_addr=token.address,
                    holder_addr=holder_address,
                    decimals=token.decimals,
                )
                wallet_balances[token.name] = balance
            except Exception as e:  # handle if contract not found in wallet
                logger.info(
                    f"Failed to get balance for {token.address} due to an error: {e}"
                )

        return wallet_balances

    @classmethod
    async def get_zklend_position(
            cls,
            contract_address: str,
            position: "Position"
    ) -> DashboardResponse:
        """
        Get the zkLend position for the given wallet ID.
        :param contract_address: contract address
        :param position: Position db model
        :return: zkLend position validated by Pydantic models
        """
        pass

    @classmethod
    def _get_products(cls, dapps: list) -> list[dict]:
        """
        Get the products from the dapps.
        :param dapps: List of dapps
        :return: List of positions
        """
        return [product for dapp in dapps for product in dapp.get("products", [])]

    @classmethod
    async def get_current_position_sum(cls, position: dict) -> Decimal:
        """
        Get the current position sum.
        :param position: Position data
        :return: current position sum
        """
        # TODO add test cases for this method
        current_prices = await cls.get_current_prices()
        try:
            result = current_prices.get(position["token_symbol"], Decimal(0)) * Decimal(
                position["amount"]
            )
            return result
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error calculating current position sum: {e}")
            return Decimal(0)

    @classmethod
    async def get_start_position_sum(cls, start_price: str, amount: str) -> Decimal:
        """
        Get the start position sum.
        :param start_price: Start price
        :param amount: Token symbol
        :return: start position sum
        """
        try:
            return Decimal(start_price) * Decimal(amount)
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error calculating start position sum: {e}")
            return Decimal(0)
