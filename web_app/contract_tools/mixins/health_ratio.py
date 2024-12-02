"""
HealthRatioMixin is a mixin class to calculate the health ratio of a deposit contract.
"""
import asyncio
from decimal import Decimal

from pragma_sdk.common.types.types import AggregationMode
from pragma_sdk.onchain.client import PragmaOnChainClient

from web_app.contract_tools.blockchain_call import StarknetClient
from web_app.contract_tools.constants import TokenParams

CLIENT = StarknetClient()
PRAGMA = PragmaOnChainClient(
    network="mainnet",
)


class HealthRatioMixin:
    """
    A mixin class to calculate the health ratio of a deposit contract.
    """

    @classmethod
    async def _get_pragma_price(cls, token: str) -> Decimal:
        """
        Get the price of a token from the Pragma API.

        :param token: The token symbol (e.g., "ETH", "USDC").
        :return: The price of the token as a Decimal.
        """
        decimals = 10**8 if token not in ("USDC", "USDT") else 10**6
        data = await PRAGMA.get_spot(f"{token}/USD", AggregationMode.MEDIAN)
        return Decimal(data.price / decimals)

    @classmethod
    async def _get_z_balances(
        cls, reserves: dict[str, tuple[int, int]], deposit_contract_address: str
    ) -> dict[str, Decimal]:
        """
        Get the balances of tokens in a deposit contract.

        :param reserves: A dictionary of token reserves with token symbols as keys
         and tuples of (decimals, address) as values.
        :param deposit_contract_address: The address of the deposit contract.
        :return: A dictionary of token balances with token symbols as keys
         and balances as Decimal values.
        """
        tasks = [
            CLIENT.get_balance(z_data[1], deposit_contract_address, z_data[0])
            for z_data in reserves.values()
        ]
        balances = {
            token: Decimal(balance)
            for token, balance in zip(reserves.keys(), await asyncio.gather(*tasks))
        }
        return balances

    @classmethod
    async def _get_deposited_tokens(
        cls, deposit_contract_address: str
    ) -> dict[str, Decimal]:
        """
        Get the deposited tokens and their amounts in a deposit contract.

        :param deposit_contract_address: The address of the deposit contract.
        :return: A dictionary of deposited tokens with token symbols as keys
         and amounts as Decimal values.
        """
        reserves = await CLIENT.get_z_addresses()
        deposits = await cls._get_z_balances(reserves, deposit_contract_address)
        return {
            token: amount * TokenParams.get_token_collateral_factor(token)
            for token, amount in deposits.items()
            if amount != 0
        }

    @classmethod
    async def _get_pragma_prices(cls, tokens: set) -> dict[str, Decimal]:
        """
        Get the prices of multiple tokens from the Pragma API.

        :param tokens: A set of token symbols.
        :return: A dictionary of token prices with token symbols as
         keys and prices as Decimal values.
        """
        tasks = [cls._get_pragma_price(token) for token in tokens]
        return {
            token: price for token, price in zip(tokens, await asyncio.gather(*tasks))
        }

    @classmethod
    async def get_health_ratio(
        cls, deposit_contract_address: str, borrowed_token: str
    ) -> str:
        """
        Calculate the health ratio of a deposit contract.

        :param deposit_contract_address: The address of the deposit contract.
        :param borrowed_token: The symbol of the borrowed token.
        :return: The health ratio as a string.
        """
        deposits = await cls._get_deposited_tokens(deposit_contract_address)
        debt_raw = await CLIENT.get_zklend_debt(
            deposit_contract_address, TokenParams.get_token_address(borrowed_token)
        )
        prices = await cls._get_pragma_prices(set(deposits.keys()) | {borrowed_token})

        deposit_usdc = sum(
            amount * Decimal(prices[token])
            for token, amount in deposits.items()
            if amount != 0
        )
        borrowed_address = TokenParams.get_token_address(borrowed_token)
        debt_usdc = (
            debt_raw[0]
            * prices[borrowed_token]
            / 10 ** int(TokenParams.get_token_decimals(borrowed_address))
        )

        return (
            f"{round(deposit_usdc / Decimal(debt_usdc), 2)}" if debt_usdc != 0 else "0"
        )


if __name__ == "__main__":
    print(
        asyncio.run(
            HealthRatioMixin.get_health_ratio(
                "0x0582d5Bc3CcfCeF2F7aF1FdA976767B010E453fF487A7FD2ccf9df1524f4D8fC",
                "ETH",
            )
        )
    )
