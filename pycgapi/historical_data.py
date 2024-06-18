import time
from datetime import datetime

import pandas as pd
import pytz
from tqdm import tqdm
from typing import Union

from .base import CoinGeckoAPI
from .utils import convert_to_unix


class HistoricalData(CoinGeckoAPI):
    def coin_historical_on_date(
        self,
        coin_id: str,
        date: str,
        localization: str = 'en'
    ) -> dict:
        """
        Retrieves historical data for a specified coin at 00:00:00 UTC
        on a given date, including price, market cap, and trading volume.

        Args:
            coin_id (str): The coin's ID (e.g., 'bitcoin'). Obtainable
                via the 'coins/list' endpoint or respective coin page.
            date (str): The date for the historical snapshot in
                dd-mm-yyyy format (e.g., '30-12-2022').
            localization (str, optional): Language preference for data
                response. Set to 'false' to exclude localized languages.
                Defaults to 'en'.

        Returns:
            dict: A dictionary containing historical data of the specified
                coin at the specified date, including price, market cap, and
                trading volume.

        Notes:
            - Endpoint: 'coins/{id}/history'.
            - Data corresponds to 00:00:00 UTC of the specified date.
            - The last completed UTC day is available 35 minutes after midnight.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-history

        """
        # Parse the date from the input format to the required format
        parsed_date = datetime.strptime(date, '%d-%m-%Y')
        formatted_date = parsed_date.strftime('%d-%m-%Y')
        endpoint = f'coins/{coin_id}/history'
        params = {
            'date': formatted_date,
            'localization': localization
        }
        response = self._get(endpoint, **params)
        return response

    def coin_historical_market_data(
        self,
        coin_id: str,
        vs_currency: str = 'usd',
        days: Union[int, str] = 30,
        interval: str = 'daily',
        precision: Union[int, str] = 'full',
        from_date: str = None,
        to_date: str = None,
        timezone_str: str = 'UTC'
    ) -> pd.DataFrame:
        """
        Retrieves historical market data for a coin, including price,
        market cap, and volume at specified intervals.

        Args:
            coin_id (str): ID of the coin, e.g., 'bitcoin'.
            vs_currency (str, optional): Currency for market data,
                default 'usd'.
            days (Union[int, str], optional): Number of days ago or 'max'.
            interval (str, optional): Data interval, default 'daily'.
            precision (Union[int, str], optional): Decimal precision or 'full'.
            from_date (str, optional): Start date, 'mm-dd-yyyy'.
            to_date (str, optional): End date, 'mm-dd-yyyy'.
            timezone_str (str, optional): Timezone, default 'UTC'.

        Returns:
            pd.DataFrame: Historical data with prices, market caps,
                and volumes, indexed by timestamp.

        Notes:
            - Endpoint: 'coins/{id}/market_chart' or
              'coins/{id}/market_chart/range'.
            - Data granularity adjusts automatically.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-market-chart

        """
        if from_date and to_date:
            from_timestamp = convert_to_unix(from_date)
            to_timestamp = convert_to_unix(to_date)
            endpoint = f'coins/{coin_id}/market_chart/range'
            params = {
                'vs_currency': vs_currency,
                'from': from_timestamp,
                'to': to_timestamp,
                'precision': str(precision)  # Convert to string
            }
        else:
            endpoint = f'coins/{coin_id}/market_chart'
            params = {
                'vs_currency': vs_currency,
                'days': str(days) if isinstance(days, int) else days,
                # Convert integer days to string
                'interval': interval,
                'precision': str(precision) if isinstance(precision,
                                                          int) else precision
                # Convert integer precision to string
            }
        response = self._get(endpoint, **params)
        df = pd.DataFrame({
            'timestamp': [item[0] for item in response['prices']],
            'price': [item[1] for item in response['prices']],
            'market_cap': [item[1] for item in response['market_caps']],
            'total_volume': [item[1] for item in response['total_volumes']]
        })
        tz = pytz.timezone(timezone_str)
        df['timestamp'] = [datetime.fromtimestamp(ts / 1000, tz=tz) for ts in
                           df['timestamp']]
        if len(df) > 1:
            df.iloc[:-1, df.columns.get_loc('timestamp')] = df.iloc[:-1][
                'timestamp'].apply(
                lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0)
            )
        df.set_index('timestamp', inplace=True)
        return df

    def multiple_coins_historical_data(
        self,
        coin_ids: list,
        vs_currency: str = 'usd',
        days: Union[int, str] = 30,
        interval: str = 'daily',
        precision: Union[int, str] = 'full',
        from_date: str = None,
        to_date: str = None,
        timezone_str: str = 'UTC'
    ) -> dict:
        """
        Retrieves historical market data for multiple coins, presented in
        separate DataFrames for prices, market caps, and volumes.

        Args:
            coin_ids (list): List of coin IDs (e.g., ['bitcoin', 'ethereum']).
            vs_currency (str, optional): Currency for market data.
            days (Union[int, str], optional): Time scope for data.
            interval (str, optional): Granularity of data, default 'daily'.
            precision (Union[int, str], optional): Precision for price values.
            from_date (str, optional): Start date in 'mm-dd-yyyy' format.
            to_date (str, optional): End date in 'mm-dd-yyyy' format.
            timezone_str (str, optional): Timezone used for data, default 'UTC'.

        Returns:
            dict: Contains DataFrames for prices, market caps, and volumes,
                  each keyed by metric and indexed by timestamp.

        Notes:
            - Endpoint: 'coins/{id}/market_chart' or
              'coins/{id}/market_chart/range'.
            - Data granularity and interval can be specified, or left
              empty for automatic adjustment.
            - Exclusively for Enterprise plan subscribers for finer
              granularity options.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-market-chart

        """
        price_dfs = []
        market_cap_dfs = []
        total_volume_dfs = []
        rate_limit = 500 if hasattr(self, 'pro_api') and self.pro_api else 10
        delay = 60 / rate_limit

        for coin_id in tqdm(coin_ids):
            time.sleep(delay)  # Respect rate limits
            data = self.coin_historical_market_data(
                coin_id, vs_currency,
                str(days) if isinstance(days, int) else days, interval,
                str(precision) if isinstance(precision, int) else precision,
                from_date, to_date, timezone_str)

            price_df = pd.DataFrame(data['price'],
                                    columns=['timestamp', coin_id])
            market_cap_df = pd.DataFrame(data['market_cap'],
                                         columns=['timestamp', coin_id])
            total_volume_df = pd.DataFrame(data['total_volume'],
                                           columns=['timestamp', coin_id])

            price_dfs.append(price_df)
            market_cap_dfs.append(market_cap_df)
            total_volume_dfs.append(total_volume_df)

        combined_price_df = pd.concat(price_dfs, axis=1).dropna()
        combined_market_cap_df = pd.concat(market_cap_dfs, axis=1).dropna()
        combined_total_volume_df = pd.concat(total_volume_dfs, axis=1).dropna()

        return {
            'price': combined_price_df,
            'market_cap': combined_market_cap_df,
            'total_volume': combined_total_volume_df
        }

    def coin_circulating_supply_history(
        self,
        coin_id: str = 'bitcoin',
        days: Union[int, str] = 'max',
        interval: str = 'daily',
        from_date: str = None,
        to_date: str = None
    ) -> pd.DataFrame:
        """
        Retrieves historical circulating supply data for a specified coin,
        either for a designated number of days or within a specific date range.

        Args:
            coin_id (str): ID of the coin (e.g., 'bitcoin').
            days (Union[int, str]): Number of days from now for historical data,
                can be an integer or 'max' for the maximum available data.
            interval (str, optional): Data granularity. Options include
                'daily', 'hourly', '5-minutely'. Defaults to 'daily'.
            from_date (str, optional): Start date for the data range in
                'mm-dd-yyyy' format.
            to_date (str, optional): End date for the data range in
                'mm-dd-yyyy' format.

        Returns:
            pd.DataFrame: A DataFrame containing the circulating supply
            data, indexed by timestamp.

        Notes:
            - Endpoint: Uses 'coins/{id}/circulating_supply_chart' for rolling
              data or 'coins/{id}/circulating_supply_chart/range' for a date
              range.
            - Data is updated every 5 minutes; last completed UTC day data
              is available 35 minutes after midnight.
            - Accessible exclusively to Enterprise Plan subscribers.
            - CoinGecko API Documentation:
              Rolling data:
                https://docs.coingecko.com/reference/coins-id-circulating-supply-chart
              Date range data:
                https://docs.coingecko.com/reference/coins-id-circulating-supply-chart-range

        """
        if from_date and to_date:
            from_timestamp = convert_to_unix(from_date)
            to_timestamp = convert_to_unix(to_date)
            endpoint = f'coins/{coin_id}/circulating_supply_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            endpoint = f'coins/{coin_id}/circulating_supply_chart'
            params = {
                'days': str(days) if isinstance(days, int) else days,
                'interval': interval
            }

        response = self._get(endpoint, **params)
        df = pd.DataFrame(
            response['circulating_supply'],
            columns=['timestamp', 'circulating_supply']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def coin_total_supply_history(
        self,
        coin_id: str,
        days: Union[int, str] = 30,
        interval: str = 'daily',
        from_date: str = None,
        to_date: str = None
    ) -> pd.DataFrame:
        """
        Retrieves historical total supply data for a coin, either for a
        specified number of days or within a defined date range.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin').
            days (Union[int, str]): Days from now to retrieve data for,
                up to 'max'. Can be an integer or 'max' for the maximum
                available data.
            interval (str): Data interval; valid values are 'daily', 'hourly',
                and '5-minutely'. Defaults to 'daily'.
            from_date (str, optional): Start date in 'mm-dd-yyyy' format.
            to_date (str, optional): End date in 'mm-dd-yyyy' format.

        Returns:
            pd.DataFrame: A DataFrame containing the total supply data of the
                specified coin, indexed by timestamp.

        Notes:
            - Endpoint: Uses 'coins/{id}/total_supply_chart' for the days
              parameter; 'coins/{id}/total_supply_chart/range' for date range.
            - Data is available 35 minutes after midnight UTC.
            - Exclusive to Enterprise Plan subscribers.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-total-supply-chart
              https://docs.coingecko.com/reference/coins-id-total-supply-chart-range

        """
        if from_date and to_date:
            from_timestamp = convert_to_unix(from_date)
            to_timestamp = convert_to_unix(to_date)
            endpoint = f'coins/{coin_id}/total_supply_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            endpoint = f'coins/{coin_id}/total_supply_chart'
            params = {
                'days': str(days) if isinstance(days, int) else days,
                'interval': interval
            }

        response = self._get(endpoint, **params)
        data = response.get('total_supply', [])
        df = pd.DataFrame(data, columns=['timestamp', 'total_supply'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
