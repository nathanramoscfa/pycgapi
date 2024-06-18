import pandas as pd

from ..base import CoinGeckoAPI


class SimpleOnChain(CoinGeckoAPI):
    def token_price_by_addresses(
        self, network: str,
        addresses: list
    ) -> pd.DataFrame:
        """
        Retrieves current USD price of tokens based on token contract
        addresses on a specified network.

        Args:
            network (str): Network ID, e.g., 'eth', 'binance-smart-chain'.
            addresses (list): Token contract addresses.

        Returns:
            pd.DataFrame: Current USD prices of specified tokens.

        Notes:
            - Endpoint combines network and token addresses to fetch prices.
            - Prices are shown in USD.
            - Addresses not found are ignored.
            - Best price pool determined by GeckoTerminal's routing.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/onchain-simple-price

        """
        addresses_str = ','.join(addresses)
        endpoint = (f"onchain/simple/networks/{network}/token_price"
                    f"/{addresses_str}")
        response = self._get(endpoint)
        token_price = response.get(
            'data', {}).get('attributes', {}).get('token_prices', {})
        df = pd.DataFrame.from_dict(
            token_price, orient='index', columns=['usd_price']
        )
        df.index.name = 'token_address'
        return df
