import pandas as pd
from typing import Union, List

from .base import CoinGeckoAPI


class Simple(CoinGeckoAPI):
    def simple_prices(
        self,
        coin_ids: Union[str, List[str]] = None,
        vs_currencies: Union[str, List[str]] = 'usd',
        include_market_cap: bool = False,
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
        include_last_updated_at: bool = False,
        precision: str = None,
        platform_id: str = None,
        contract_addresses: List[str] = None
    ) -> pd.DataFrame:
        """
        Retrieves current prices for cryptocurrencies from the CoinGecko API
        by coin IDs or via contract addresses on a specified platform.

        Args:
            coin_ids (Union[str, List[str]]): IDs for querying coin prices.
            vs_currencies (Union[str, List[str]]): Currencies for price data.
            include_market_cap (bool): If True, includes market cap data.
            include_24hr_vol (bool): If True, includes 24-hour volume data.
            include_24hr_change (bool): If True, includes 24-hour price change.
            include_last_updated_at (bool): If True, includes the last update
                time.
            precision (str): Decimal precision for price values. Options are
                '0' to '18' for token prices.
            platform_id (str): Platform ID for querying token prices.
            contract_addresses (List[str]): Addresses for querying token prices.

        Returns:
            pd.DataFrame: Contains the requested price data and additional info.

        Notes:
            - Endpoints: 'simple/price' and 'simple/token_price/{platform_id}'.
            - Data updates every 30 seconds for Pro API users.
            - Cache and data update frequency is every 30 seconds.
            - Check CoinGecko for network-specific prices and API documentation:
              https://docs.coingecko.com/reference/simple-price
              https://docs.coingecko.com/reference/simple-token-price

        """
        if platform_id and contract_addresses:
            endpoint = f'simple/token_price/{platform_id}'
            params = {
                'contract_addresses': ','.join(contract_addresses),
                'vs_currencies': ','.join(vs_currencies)
            }
        else:
            endpoint = 'simple/price'
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': ','.join(vs_currencies)
            }

        optional_params = {
            'include_market_cap': include_market_cap,
            'include_24hr_vol': include_24hr_vol,
            'include_24hr_change': include_24hr_change,
            'include_last_updated_at': include_last_updated_at
        }
        params.update({k: str(v).lower() for k, v in optional_params.items() if
                       v is not None})

        if precision:
            params['precision'] = precision

        response = self._get(endpoint, **params)
        return pd.DataFrame.from_dict(response, orient='index')

    def supported_currencies(self):
        """
        Retrieves a list of currencies that can be used for price conversion
        in various API endpoints on CoinGecko.

        Returns:
            list: A list of currency identifiers supported by CoinGecko.

        Notes:
            - Endpoint: 'simple/supported_vs_currencies'.
            - The endpoint provides fiat currencies and cryptocurrencies.
            - Data is cached and updated every 30 seconds.
            - Available for public and pro API users.
            - API Documentation:
              https://docs.coingecko.com/reference/simple-supported-currencies

        """
        response = self._get("simple/supported_vs_currencies")
        return response
