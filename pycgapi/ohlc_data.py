import time

import pandas as pd
from tqdm import tqdm
from typing import Union

from .base import CoinGeckoAPI


class OHLCData(CoinGeckoAPI):
    def coin_ohlc_data(
        self,
        coin_id: str,
        vs_currency: str = 'usd',
        days: Union[int, str] = 30,
        precision: str = None
    ) -> pd.DataFrame:
        """
        Fetches OHLC (Open, High, Low, Close) data for a specified
        cryptocurrency, providing detailed price points over selected days.

        Args:
            coin_id (str): ID of the coin (e.g., 'bitcoin'). Refer to
                '/coins/list' for valid IDs.
            vs_currency (str, optional): Target currency for market data,
                such as 'usd'. Defaults to 'usd'.
            days (Union[int, str], optional): Number of days up to 'max' to
                retrieve data for. Valid values: 1, 7, 14, 30, 90, 180,
                'max'. Defaults to 30.
            precision (str, optional): Decimal precision of price values.

        Returns:
            pd.DataFrame: Contains columns for Timestamp, Open, High, Low,
                and Close prices, indexed by Timestamp.

        Notes:
            - Endpoint: 'coins/{id}/ohlc'.
            - Data granularity adjusts automatically based on the duration:
              1-2 days: 30 minutes, 3-30 days: 4 hours, 31+ days: 4 days.
            - 'daily' interval is exclusive for Paid Plan Subscribers and
              available for durations of 1, 7, 14, 30, 90, and 180 days.
            - Updated every 30 minutes, accessible 35 minutes after
              midnight UTC.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-ohlc

        """
        endpoint = f"coins/{coin_id}/ohlc"
        params = {
            'vs_currency': vs_currency,
            'days': str(days)
        }
        if precision:
            params['precision'] = precision

        response = self._get(endpoint, **params)
        df = pd.DataFrame(response,
                          columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)
        return df

    def multiple_coins_ohlc_data(
        self,
        coin_ids: list,
        vs_currency: str = 'usd',
        days: Union[int, str] = 30,
        precision: str = None
    ) -> dict:
        """
        Fetches OHLC (Open, High, Low, Close) data for multiple coins,
        returning a dictionary where each key corresponds to an OHLC component
        and its value is a DataFrame with that component's data for each coin.

        Args:
            coin_ids (list): List of coin IDs (e.g., ['bitcoin', 'ethereum']).
            vs_currency (str, optional): Currency for market data,
                defaults to 'usd'. See /simple/supported_vs_currencies for
                options.
            days (Union[int, str], optional): Time frame for data retrieval;
                valid values are 1, 7, 14, 30, 90, 180, 'max'. Defaults to 30.
            precision (str, optional): Decimal precision of price data.

        Returns:
            dict: Contains DataFrames indexed by OHLC components ('Open',
                'High', 'Low', 'Close') with columns for each coin_id.

        Notes:
            - Uses endpoint 'coins/{id}/ohlc' for each coin.
            - Data updates every 30 minutes, accessible 35 minutes after
              midnight UTC.
            - Daily candle interval available exclusively for paid subscribers,
              applicable for 1, 7, 14, 30, 90, and 180 days.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-ohlc

        """
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'
        ohlc_data = {'Open': pd.DataFrame(), 'High': pd.DataFrame(),
                     'Low': pd.DataFrame(), 'Close': pd.DataFrame()}

        rate_limit = 500 if self.pro_api else 10
        delay = 60 / rate_limit

        for coin_id in coin_ids:
            time.sleep(delay)  # Comply with rate limits
            df = self.coin_ohlc_data(coin_id, vs_currency, days, precision)

            for column in ['Open', 'High', 'Low', 'Close']:
                if column in df.columns:
                    ohlc_data[column][coin_id] = df[column]

        return ohlc_data
