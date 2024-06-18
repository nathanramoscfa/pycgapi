import pandas as pd
from typing import Optional, Union

from .base import CoinGeckoAPI
from .utils import convert_to_unix


class Exchanges(CoinGeckoAPI):
    def active_exchanges_list(
        self,
        per_page: int = 100,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches a list of all active exchanges from the CoinGecko API,
        including trading volume information.

        Args:
            per_page (int, optional): Number of results per page, with a
                maximum of 250. Defaults to 100.
            page (int, optional): Page number for results pagination.
                Defaults to 1.

        Returns:
            pd.DataFrame: Contains details of active exchanges, including
                their ids, names, and trading volumes.

        Notes:
            - Endpoint: 'exchanges'.
            - Data updates every 60 seconds.
            - Pagination is supported, allowing navigation across multiple
              pages of data.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/exchanges

        """
        endpoint = 'exchanges'
        params = {'per_page': per_page, 'page': page}
        response = self._get(endpoint, **params)
        return pd.DataFrame(response)

    def all_exchanges_list(self) -> pd.DataFrame:
        """
        Retrieves a complete list of all supported market exchanges from
        the CoinGecko API, including their unique IDs and names.

        Returns:
            pd.DataFrame: Contains the IDs and names of all supported market
                exchanges listed on CoinGecko.

        Notes:
            - Endpoint: 'exchanges/list'.
            - Data updates every 5 minutes, ensuring current information.
            - No pagination required, as all exchanges are returned in a
              single call.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/exchanges-list

        """
        endpoint = 'exchanges/list'
        response = self._get(endpoint)
        return pd.DataFrame(response)

    def exchange_volume_data(self, exchange_id: str = 'gdax') -> dict:
        """
        Fetches trading volume in BTC and the top 100 tickers for a specific
        exchange from the CoinGecko API.

        Args:
            exchange_id (str, optional): The unique identifier of the exchange
                to retrieve data for, such as 'binance'. Default is 'gdax'.
                Exchange IDs can be obtained from the get_supported_exchanges
                endpoint.

        Returns:
            dict: Contains detailed information about the exchange, including
                volume in BTC and data on the top 100 tickers.

        Notes:
            - Endpoint: 'exchanges/{exchange_id}'.
            - Data includes name, year established, country, exchange volume
              in BTC, and details on the top 100 tickers.
            - Tickers are limited to 100 items; for additional tickers,
              use the '/exchanges/{id}/tickers' endpoint.
            - Data is refreshed every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/exchanges-id

        """
        endpoint = f'exchanges/{exchange_id}'
        response = self._get(endpoint)
        return response

    def exchange_market_tickers(
        self,
        exchange_id: str,
        coin_ids: Optional[str] = None,
        include_exchange_logo: bool = False,
        page: int = 1,
        depth: bool = False,
        order: str = "trust_score_desc"
    ) -> pd.DataFrame:
        """
        Fetches tickers for a specific exchange with various filtering
        and sorting options.

        Args:
            exchange_id (str): ID of the exchange (e.g., 'binance').
            coin_ids (Optional[str], optional): Comma-separated list of coin IDs
                to filter tickers. Defaults to None.
            include_exchange_logo (bool, optional): If True, includes the
                exchange logos in the results. Defaults to False.
            page (int, optional): Page number for results pagination.
                Defaults to 1.
            depth (bool, optional): If True, includes 2% orderbook depth.
                Defaults to False.
            order (str, optional): Criteria for sorting the results.
                 Options include: 'trust_score_desc', 'trust_score_asc',
                 'volume_desc', 'volume_asc'. Defaults to 'trust_score_desc'.

        Returns:
            pd.DataFrame: A DataFrame containing the tickers from the specified
                exchange that meet the filter criteria. Each row includes ticker
                details such as market, price, volume, and more.

        Notes:
            - Endpoint: 'exchanges/{exchange_id}/tickers'.
            - Responses are paginated to 100 items per page.
            - 'is_stale' indicates tickers not updated for over 8 hours;
              'is_anomaly' indicates outlier prices.
            - Data updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/exchanges-id-tickers

        """
        endpoint = f'exchanges/{exchange_id}/tickers'
        params = {
            'coin_ids': coin_ids,
            'include_exchange_logo': "true"
            if include_exchange_logo else "false",
            'page': page,
            'depth': "true" if depth else "false",
            'order': order
        }
        response = self._get(endpoint, **params)
        return pd.DataFrame(response['tickers'])

    def exchange_historical_volume(
        self,
        exchange_id: str = 'gdax',
        days: Union[int, str] = 30,
        from_date: str = None,
        to_date: str = None
    ) -> pd.DataFrame:
        """
        Retrieves historical trading volume in BTC for a specified
        exchange, with options for rolling or specific date range data.

        Args:
            exchange_id (str, optional): ID of the exchange, e.g., 'binance'.
                Default is 'gdax'.
            days (Union[int, str], optional): Number of days for rolling data,
                up to 90 days. Defaults to 30.
            from_date (str, optional): Start date in 'mm-dd-yyyy' format for
                specific date range.
            to_date (str, optional): End date in 'mm-dd-yyyy' format for
                specific date range.

        Returns:
            pd.DataFrame: Data with timestamps and volumes over the selected
                period, indexed by timestamp.

        Notes:
            - Endpoint: Uses 'exchanges/{id}/volume_chart' for rolling data or
              'exchanges/{id}/volume_chart/range' for a date range.
            - Data granularity auto-adjusts based on the period:
              1 day = 10-minutely, 2-90 days = hourly, 91+ days = daily.
            - Date range for 'volume_chart/range' should not exceed 31 days.
            - Updated every 60 seconds for rolling data, every 5 minutes for
              date range data.
            - CoinGecko API Documentation:
              Rolling data:
                https://docs.coingecko.com/reference/exchanges-id-volume-chart
              Date range data:
                https://docs.coingecko.com/reference/exchanges-id-volume-chart-range

        """
        if from_date and to_date:
            from_timestamp = convert_to_unix(from_date)
            to_timestamp = convert_to_unix(to_date)
            if (to_timestamp - from_timestamp) > (31 * 24 * 3600):
                raise ValueError("Date range should not exceed 31 days.")

            endpoint = f'exchanges/{exchange_id}/volume_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            endpoint = f'exchanges/{exchange_id}/volume_chart'
            params = {'days': days}

        response = self._get(endpoint, **params)
        df = pd.DataFrame(response, columns=['timestamp', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df.astype(float)
