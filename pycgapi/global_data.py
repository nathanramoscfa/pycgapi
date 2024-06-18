import pandas as pd
from typing import Union

from .base import CoinGeckoAPI


class GlobalData(CoinGeckoAPI):
    def global_crypto_stats(self) -> dict:
        """
        Fetches comprehensive global cryptocurrency data from the CoinGecko API,
        including overall metrics, market cap percentages, and total volumes.

        Returns:
            dict: A dictionary containing:
                - 'global_data': DataFrame with overall global metrics.
                - 'market_cap_percentage': DataFrame with market cap percentages
                  by cryptocurrency.
                - 'total_market_cap': DataFrame with total market caps across
                  all cryptocurrencies.
                - 'total_volume': DataFrame with total trading volumes.

        Notes:
            - Endpoint: 'global'.
            - Data is updated every 10 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/crypto-global

        """
        endpoint = 'global'
        response = self._get(endpoint)
        data = response['data']

        # Parsing data into separate DataFrames
        global_data = pd.DataFrame.from_dict(
            {k: v for k, v in data.items() if k not in ['market_cap_percentage',
                                                        'total_market_cap',
                                                        'total_volume']},
            orient='index', columns=['Value']
        )

        market_cap_percentage = pd.DataFrame(
            list(data['market_cap_percentage'].items()),
            columns=['Currency', 'Percentage'])

        total_market_cap = pd.DataFrame(list(data['total_market_cap'].items()),
                                        columns=['Currency', 'Market Cap'])

        total_volume = pd.DataFrame(list(data['total_volume'].items()),
                                    columns=['Currency', 'Volume'])

        return {
            'global_data': global_data,
            'market_cap_percentage': market_cap_percentage,
            'total_market_cap': total_market_cap,
            'total_volume': total_volume
        }

    def global_defi_stats(self) -> pd.DataFrame:
        """
        Fetches global decentralized finance (DeFi) data from the
        CoinGecko API, including market capitalization and trading volume.

        Returns:
            pd.DataFrame: A DataFrame containing key DeFi metrics such
            as market cap in USD, Ethereum market cap, DeFi to Ethereum
            ratio, 24-hour trading volume, DeFi dominance, and top DeFi
            coin data.

        Notes:
            - Endpoint: 'global/decentralized_finance_defi'.
            - Data updates every 60 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/global-defi

        """
        endpoint = 'global/decentralized_finance_defi'
        response = self._get(endpoint)
        data = response['data']
        df = pd.DataFrame(list(data.items()),
                          columns=['Key', 'Value'])
        df.set_index('Key', inplace=True)
        return df

    def historical_global_market_cap(
        self,
        days: Union[int, str] = 'max',
        vs_currency: str = 'usd'
    ) -> tuple:
        """
        Fetches historical global market cap and volume data, adjusted for
        currency and time range from the CoinGecko API.

        Args:
            days (Union[int, str], optional): The number of days from now for
                which to retrieve historical data. Can be an integer or 'max'.
                Defaults to 'max'.
            vs_currency (str, optional): The target currency for market data,
                e.g., 'usd', 'eur'. Defaults to 'usd'.

        Returns:
            tuple: Contains two DataFrames; the first with historical global
                market cap data and the second with volume data, both indexed
                by timestamp.

        Notes:
            - Endpoint: 'global/market_cap_chart'.
            - Data granularity auto-adjusts based on the time range:
              1 day = hourly data, 2+ days = daily data.
            - Exclusive for all Paid Plan Subscribers.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/global-market-cap-chart

        """
        endpoint = 'global/market_cap_chart'
        params = {'days': days, 'vs_currency': vs_currency}
        response = self._get(endpoint, **params)
        market_cap_data = response['data']['market_cap']
        volume_data = response['data']['volume']

        # Convert to DataFrame and set datetime format for index
        market_cap_df = pd.DataFrame(market_cap_data,
                                     columns=['timestamp', 'market_cap'])
        volume_df = pd.DataFrame(volume_data, columns=['timestamp', 'volume'])
        market_cap_df['timestamp'] = pd.to_datetime(market_cap_df['timestamp'],
                                                    unit='ms')
        volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'],
                                                unit='ms')
        market_cap_df.set_index('timestamp', inplace=True)
        volume_df.set_index('timestamp', inplace=True)

        return market_cap_df, volume_df
