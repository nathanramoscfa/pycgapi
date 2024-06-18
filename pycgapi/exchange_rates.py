import pandas as pd

from .base import CoinGeckoAPI


class ExchangeRates(CoinGeckoAPI):
    def btc_exchange_rates(self) -> pd.DataFrame:
        """
        Retrieves current exchange rates where Bitcoin (BTC) is the base
        currency, from various global currencies using the CoinGecko API.

        Returns:
            pd.DataFrame: A DataFrame listing exchange rates between BTC and
                other currencies, including fiat and cryptocurrencies.

        Notes:
            - Endpoint: 'exchange_rates'.
            - Data updates every 5 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/exchange-rates

        """
        endpoint = 'exchange_rates'
        response = self._get(endpoint)
        data = response.get('rates', {})
        return pd.DataFrame.from_dict(
            data, orient='index'
        ).reset_index().rename(
            columns={'index': 'currency', 'value': 'rate'}
        )
