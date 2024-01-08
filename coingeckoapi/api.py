import math
import time
import pytz
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Union, Optional, Tuple
from . import utils


class CoinGeckoAPI:
    """A Python wrapper for the CoinGecko API with a focus on ease of use and data integrity.

    This class provides methods for accessing the CoinGecko API.

    Attributes:
        api_key (str): API key for the CoinGecko API.
        pro_api (bool): Flag to use the PRO API.
        base_url (str): Base URL for the CoinGecko API.
        session (requests.Session): A requests Session object for making HTTP requests.

    """
    API_BASE_URL = 'https://api.coingecko.com/api/v3/'
    PRO_API_BASE_URL = 'https://pro-api.coingecko.com/api/v3/'

    def __init__(self, api_key: str = None, pro_api: bool = False, retries: int = 5) -> None:
        """Initialize the CoinGecko API object

        Args:
            api_key (str, optional): API key for the CoinGecko API. Required if pro_api is True.
            pro_api (bool, optional): Flag to use the PRO API. If False, uses Public API. Defaults to False.
            retries (int, optional): Number of retries for failed requests. Defaults to 5.

        Returns:
            None

        """
        self.api_key = api_key
        self.pro_api = pro_api
        self.base_url = self.PRO_API_BASE_URL if self.pro_api else self.API_BASE_URL
        self.session = requests.Session()

        retries = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)

    def build_endpoint(self, endpoint: str) -> str:
        """Constructs the complete endpoint URL with API key if required.

        Args:
            endpoint (str): The specific API endpoint.

        Returns:
            str: The complete URL to be used for the API call.

        """
        if self.pro_api:
            return f'{self.base_url}{endpoint}?x_cg_pro_api_key={self.api_key}'
        else:
            return f'{self.base_url}{endpoint}'

    def end_session(self) -> str:
        """Closes the HTTP session.

        Returns:
            str: A message indicating the status of the session closure.

        """
        try:
            self.session.close()
            return "Session closed successfully."
        except Exception as e:
            return f"Error closing session: {e}"

    # ---------- PING ---------- #
    def status_check(self) -> dict:
        """Check API server status

        Returns:
            dict: API server status

        """
        complete_endpoint = self.build_endpoint('ping')
        return self.session.get(complete_endpoint).json()

    # ---------- SIMPLE ---------- #
    def simple_prices(self, coin_ids: list = None, vs_currencies: list = 'usd', include_market_cap: bool = False,
                      include_24hr_vol: bool = False, include_24hr_change: bool = False,
                      include_last_updated_at: bool = False, precision: str = None,
                      platform_id: str = None, contract_addresses: list = None) -> pd.DataFrame:
        """Get the current prices of specified cryptocurrencies in the desired currencies.

        This method fetches current prices from the CoinGecko API for cryptocurrencies by either coin_ids or with
        platform_id and contract_addresses specified. Specifying platform_id and contract_addresses queries prices
        using their contract addresses on a specified platform. Otherwise, a list of coin_ids must be specified.

        Args:
            coin_ids (str or list): A single coin ID or list of coin IDs for cryptocurrencies
                (e.g., 'bitcoin' or ['bitcoin', 'ethereum']). Refers to coins listed using the get_coin_list method.
            vs_currencies (str or list, optional): A single target currency or list of target currencies for price
                conversion (e.g., 'usd' or ['usd', 'eur']). Refers to supported vs_currencies. Defaults to 'usd'.
            include_market_cap (bool, optional): Include market cap in the response. Defaults to False.
            include_24hr_vol (bool, optional): Include 24-hour volume. Defaults to False.
            include_24hr_change (bool, optional): Include 24-hour price change. Defaults to False.
            include_last_updated_at (bool, optional): Include the last updated timestamp of the price.
                Defaults to False.
            precision (str, optional): Specify decimal precision for currency price value, ranging from 0 to 18.
                Defaults to full precision.
            platform_id (str, optional): ID of the platform issuing tokens (e.g., 'ethereum').
                See asset_platforms endpoint for options. Required for querying token prices.
            contract_addresses (list, optional): Contract addresses of tokens, comma-separated.
                Required for querying token prices.

        Returns:
            pd.DataFrame: A DataFrame containing the current prices and additional requested data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The method returns the global average price aggregated across all active exchanges.
            - It does not return the price of a specific network; cross-check on CoinGecko.com for network-specific
              prices.
            - Data is cached and updated every 60 seconds (30 seconds for Pro API users).
            - The 'include_24hr_change=true' parameter can be used to check if the 24-hour change returns a 'null'
              value.
            - Prices are returned in the specified vs_currencies.
            - The method supports both cryptocurrencies and token prices via contract addresses.
            - Works with the simple/price endpoint.
            - Available for public and pro API users.

        """
        if platform_id and contract_addresses:
            endpoint = f'simple/token_price/{platform_id}'
            params = {
                'contract_addresses': ','.join(contract_addresses) if isinstance(contract_addresses,
                                                                                 list) else contract_addresses,
                'vs_currencies': ','.join(vs_currencies) if isinstance(vs_currencies, list) else vs_currencies
            }
        else:
            endpoint = 'simple/price'
            params = {
                'ids': ','.join(coin_ids) if isinstance(coin_ids, list) else coin_ids,
                'vs_currencies': ','.join(vs_currencies) if isinstance(vs_currencies, list) else vs_currencies
            }

        params.update({
            'include_market_cap': str(include_market_cap).lower(),
            'include_24hr_vol': str(include_24hr_vol).lower(),
            'include_24hr_change': str(include_24hr_change).lower(),
            'include_last_updated_at': str(include_last_updated_at).lower()
        })

        if precision:
            params['precision'] = precision

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        # Convert the JSON response into a DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        return df

    def supported_currencies(self) -> list:
        """Fetch the list of supported vs_currencies (versus currencies) from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all supported currencies
        against which cryptocurrency prices can be compared.

        Returns:
            list: A list of supported versus currencies.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The data is updated every 60 seconds.
            - Works with the simple/supported_vs_currencies endpoint.
            - Available for public and pro API users.

        """
        complete_endpoint = self.build_endpoint("simple/supported_vs_currencies")
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Raise an exception for HTTP error codes
        return response.json()

    # ---------- COINS ---------- #
    def coins_list(self, include_platform: bool = False) -> pd.DataFrame:
        """Get a list of all supported coins with their id, name, and symbol from CoinGecko.

        Only active coins listed by the CoinGecko team are included. Inactive or deactivated
        coins are removed from the list. The list is updated every 5 minutes.

        Args:
            include_platform (bool, optional): Flag to include platform contract addresses
                (e.g., Ethereum based tokens). Defaults to False. Set to True to include platform information.

        Returns:
            pd.DataFrame: A DataFrame where each row contains the id, name, and symbol of a coin.
                If 'include_platform' is True, platform contract addresses are also included.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coin/list endpoint.
            - Available for public and pro API users.

        """
        complete_endpoint = self.build_endpoint('coins/list')
        params = {'include_platform': include_platform}
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP error codes
        data = response.json()
        df = pd.DataFrame(data)
        df.set_index('id', inplace=True)
        return df

    def coins_market_data(self, vs_currency: str = 'usd', ids: str = None, category: str = None,
                          order: str = "market_cap_desc", per_page: int = 100, page: int = 1,
                          sparkline: bool = False, price_change_percentage: str = None,
                          locale: str = "en", precision: str = None) -> pd.DataFrame:
        """Get a list of all supported coins with market data from CoinGecko.

        This method obtains all the coins' market data including price, market cap, and volume.
        The data is updated every 45 seconds. When both 'category' and 'ids' parameters are
        supplied, 'category' takes precedence over 'ids'.

        Args:
            vs_currency (str, optional): The target currency of market data (e.g., 'usd', 'eur', 'jpy', etc.).
                Default is 'usd'.
            ids (str, optional): Comma-separated cryptocurrency symbols (base). Refer to get_coins_list method.
            category (str, optional): Filter by coin category. Refer to get_coin_categories.
            order (str, optional): Sorting order. Default is "market_cap_desc". Valid values include
                'market_cap_asc', 'market_cap_desc', 'volume_asc', 'volume_desc', 'id_asc', 'id_desc'.
            per_page (int, optional): Total results per page. Default is 100. Valid range is 1 to 250.
            page (int, optional): Page through results. Default is 1.
            sparkline (bool, optional): Include sparkline 7 days data. Default is False.
            price_change_percentage (str, optional): Include price change percentage in 1h, 24h, 7d, 14d, 30d, 200d, 1y.
                Comma-separated values, invalid values will be discarded.
            locale (str, optional): Locale setting for language preferences. Default is 'en'. Valid values include
                'ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hi', 'hr', 'hu', 'id',
                'it', 'ja', 'ko', 'lt', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr',
                'uk', 'vi', 'zh', 'zh-tw'.
            precision (str, optional): Decimal precision for currency price value. Optional. Valid values are 0-18.

        Returns:
            pd.DataFrame: A DataFrame containing the market data of coins, with columns for each specified field.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/markets endpoint.
            - Available for public and pro API users.

        """
        complete_endpoint = self.build_endpoint('coins/markets')
        params = {
            'vs_currency': vs_currency,
            'ids': ids,
            'category': category,
            'order': order,
            'per_page': per_page,
            'page': page,
            'sparkline': sparkline,
            'price_change_percentage': price_change_percentage,
            'locale': locale,
            'precision': precision
        }
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df.set_index('id', inplace=True)
        return df

    def top_coins_market_data(self, top_n: int = 250) -> pd.DataFrame:
        """Fetch market data for the top N cryptocurrencies by market cap.

        This method paginates through the CoinGecko API to retrieve the market data
        for the specified number of top cryptocurrencies.

        Args:
            top_n (int, optional): The number of top cryptocurrencies to fetch. Default is 250.

        Returns:
            pd.DataFrame: A DataFrame containing the market data of the top N cryptocurrencies.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/markets endpoint.
            - Available for public and pro API users.

        """
        per_page = 250  # Max per page
        total_pages = math.ceil(top_n / per_page)
        all_coins_df = pd.DataFrame()

        # Rate limiting
        rate_limit = 500 if self.pro_api else 10  # 500 req/min for Pro, 30 req/min for others
        delay = 60 / rate_limit  # Calculate delay based on rate limit

        for page in range(1, total_pages + 1):
            time.sleep(delay)  # Delay the request based on the rate limit
            page_df = self.coins_market_data(per_page=per_page, page=page)
            all_coins_df = pd.concat([all_coins_df, page_df], ignore_index=True)

            if len(all_coins_df) >= top_n:  # Break if we have fetched enough coins
                break

        return all_coins_df.iloc[:top_n]  # Ensure only top_n rows are returned

    def coin_info(self, coin_id: str, localization: str = 'true', tickers: bool = True,
                  market_data: bool = True, community_data: bool = True,
                  developer_data: bool = True, sparkline: bool = False) -> dict:
        """Get current data (name, price, market, etc.) for a specified coin from CoinGecko.

        This method retrieves a wide array of data for a specified cryptocurrency, including
        name, price, market data, tickers, community and developer data. The data is updated every
        60 seconds, ensuring up-to-date information. Twitter, Telegram, and Reddit data is updated daily.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin'). Refers to coins listed in the get_coins_list method.
            localization (str, optional): Include all localized languages in response. Defaults to 'true'.
            tickers (bool, optional): Include ticker data, limited to 100 items. For more, use the get_coin_tickers
                method. Defaults to True.
            market_data (bool, optional): Include market data. Defaults to True.
            community_data (bool, optional): Include community data. Defaults to True.
            developer_data (bool, optional): Include developer data. Defaults to True.
            sparkline (bool, optional): Include sparkline data for the last 7 days. Defaults to False.

        Returns:
            dict: A dictionary containing the data for the coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Ticker data has limitations: 'is_stale' is true if not updated for > 8 hours; 'is_anomaly' if price is an
              outlier.
            - Users are responsible for managing how to display ticker information (e.g., footnote, opacity).
            - For stale prices, refer to 'last_updated' in the price information.
            - Works with the coins/{id} endpoint.
            - Available for public and pro API users.

        """
        complete_endpoint = self.build_endpoint(f'coins/{coin_id}')
        params = {
            'localization': localization,
            'tickers': tickers,
            'market_data': market_data,
            'community_data': community_data,
            'developer_data': developer_data,
            'sparkline': sparkline
        }
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def coin_market_tickers(self, coin_id: str, exchange_ids: str = None, include_exchange_logo: bool = False,
                            page: int = 1, order: str = 'trust_score_desc', depth: bool = False) -> pd.DataFrame:
        """Get tickers for a specific coin, paginated to 100 items per page.

        This method retrieves ticker information for a specified cryptocurrency, with the
        data updated every 2 minutes. It includes details such as price, volume, and last trading time.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin'). Refers to coins listed in the get_coins_list method.
            exchange_ids (str, optional): Comma separated cryptocurrency exchange ids (e.g., 'binance,kraken').
            include_exchange_logo (bool, optional): Flag to include exchange logo. Defaults to False.
            page (int, optional): Page through results. Default is 1.
            order (str, optional): Sort results by field. Default is "trust_score_desc".
            depth (bool, optional): Flag to include 2% orderbook depth. Defaults to False.

        Returns:
            pd.DataFrame: A dictionary containing the tickers for the specified coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Ticker is marked as 'stale' if not updated for more than 8 hours and as 'anomaly' if price is an outlier.
            - Users are responsible for managing the display of these information (e.g., footnote, opacity).
            - Includes last unconverted price, 24h trading volume, converted prices and volumes in BTC, ETH, and USD.
            - The 'last_traded_at' and 'last_fetch_at' fields indicate the last time the price changed and the last API
              call.
            - Works with the coins/{id}/tickers endpoint.
            - Available for public and pro API users.

        """
        complete_endpoint = self.build_endpoint(f'coins/{coin_id}/tickers')
        params = {
            'exchange_ids': exchange_ids,
            'include_exchange_logo': include_exchange_logo,
            'page': page,
            'order': order,
            'depth': depth
        }
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['tickers'])
        return df

    def coin_historical_on_date(self, coin_id: str, date: str, localization: str = 'en') -> dict:
        """Get historical data (price, market cap, 24hr volume, etc.) for a coin on a specified date.

        This method retrieves a snapshot of historical data for a given cryptocurrency at 00:00:00 UTC of the
        specified date. The last completed UTC day's data is available 35 minutes after midnight on the next
        UTC day (00:35).

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin'). Refers to coins listed in the get_coins_list method.
            date (str): The date for the historical data snapshot in mm-dd-yyyy format (e.g., '12-30-2022').
            localization (str, optional): The language setting for localization. Default is 'en'. Set to 'false' to
                exclude localized languages.

        Returns:
            dict: A dictionary containing the historical data of the specified coin at the given date.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The returned data includes price, market cap, and 24-hour trading volume.
            - Data is provided for the specified date at 00:00:00 UTC.
            - The 'date' parameter should now be formatted in mm-dd-yyyy (e.g., 12-30-2022).
            - Works with the coins/{id}/history endpoint.
            - Available for public and pro API users.

        """
        # Convert date from mm-dd-yyyy to dd-mm-yyyy
        formatted_date = datetime.strptime(date, '%m-%d-%Y').strftime('%d-%m-%Y')

        complete_endpoint = self.build_endpoint(f'coins/{coin_id}/history')
        params = {
            'date': formatted_date,
            'localization': localization
        }
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def coin_historical_market_data(self, coin_id: str, vs_currency: str = 'usd', days: Union[int, str] = 'max',
                                    interval: str = 'daily', precision: str = 'full', from_date: str = None,
                                    to_date: str = None, timezone_str: str = 'UTC') -> pd.DataFrame:
        """Get historical market data including price, market cap, and 24h volume for a coin.

        This method fetches historical market data for a given cryptocurrency. The data granularity is automatic and
        varies based on the 'days' parameter:

        - 1 day: 5-minute intervals,
        - 2 to 90 days: hourly data,
        - More than 90 days: daily data at 00:00 UTC.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin'). Refers to coins listed in get_coin_list method.
            vs_currency (str, optional): The target currency of market data ('usd', 'eur', 'jpy', etc.).
                Refers to supported vs_currencies. Defaults to 'usd'. Required.
            days (Union[int, str], optional): Data up to a number of days ago or 'max' for maximum available data.
                Default is 'max'.
            interval (str, optional): Data interval. Possible value: 'daily'. Default is 'daily'.
            precision (str, optional): Decimal precision for currency price value. Default is 'full'.
            from_date (str, optional): From date in 'mm-dd-yyyy' format or UNIX Timestamp.
            to_date (str, optional): To date in 'mm-dd-yyyy' format or UNIX Timestamp.
            timezone_str (str, optional): Timezone of the dates. Default is 'UTC'.

        Returns:
            pd.DataFrame: A DataFrame containing the historical market data of the specified coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Cache expiration times vary: 30 seconds for 1 day, 30 minutes for 2-90 days, and 12 hours for more than
              90 days.
            - The last completed UTC day's data is available 35 minutes after midnight on the next UTC day (00:35), and
              the cache always expires at 00:40 UTC.
            - Works with the coins/{id}/market_chart and coins/{id}/market_chart/range endpoints.
            - Available for public and pro API users.

        """
        # Convert the dates to UNIX timestamps
        from_timestamp = utils.convert_to_unix(from_date)
        to_timestamp = utils.convert_to_unix(to_date)

        # Handling the days parameter
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'

        if from_timestamp is not None and to_timestamp is not None:
            endpoint = f'coins/{coin_id}/market_chart/range'
            params = {
                'vs_currency': vs_currency,
                'from': from_timestamp,
                'to': to_timestamp,
                'precision': precision
            }
        else:
            endpoint = f'coins/{coin_id}/market_chart'
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': interval,
                'precision': precision
            }

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        # Convert the data to a DataFrame
        df = pd.DataFrame({
            'timestamp': [item[0] for item in data['prices']],
            'price': [item[1] for item in data['prices']],
            'market_cap': [item[1] for item in data['market_caps']],
            'total_volume': [item[1] for item in data['total_volumes']]
        })

        # Convert the UNIX timestamps to datetime in the specified timezone
        tz = pytz.timezone(timezone_str)
        df['timestamp'] = [datetime.fromtimestamp(ts / 1000, tz=tz) for ts in df['timestamp']]

        # Adjust all timestamps to midnight, except for the last entry
        if len(df) > 1:
            df.iloc[:-1, df.columns.get_loc('timestamp')] = df.iloc[:-1]['timestamp'].apply(
                lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0)
            )
        df.set_index('timestamp', inplace=True)
        return df

    def multiple_coins_historical_data(self, coin_ids: list, vs_currency: str = 'usd', days: Union[int, str] = 'max',
                                       interval: str = 'daily', precision: str = 'full', from_date: str = None,
                                       to_date: str = None, timezone_str: str = 'UTC') -> dict:
        """Get historical market data for multiple coins and separate the data into different DataFrames.

        Args:
            coin_ids (list): List of coin IDs (e.g., ['bitcoin', 'ethereum', 'tether']). Refers to coins listed in
                get_coins_list method. Required.
            vs_currency (str, optional): The target currency of market data (usd, eur, jpy, etc.). Default is 'usd'.
            days (Union[int, str], optional): Data up to a number of days ago or 'max' for maximum available data.
                Default is 'max'.
            interval (str, optional): Data interval. Possible value: 'daily'.
            precision (str, optional): Decimal precision for currency price value. Defaults to 'full'.
            from_date (str, optional): From date in 'mm-dd-yyyy' format or UNIX Timestamp. Default is None.
            to_date (str, optional): To date in 'mm-dd-yyyy' format or UNIX Timestamp. Default is None.
            timezone_str (str, optional): Timezone of the dates. Default is 'UTC'.

        Returns:
            dict: A dictionary containing DataFrames for prices, market caps, and total volumes. Each DataFrame's
                  columns represent different coins.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Cache expiration times vary: 30 seconds for 1 day, 30 minutes for 2-90 days, and 12 hours for more than
              90 days.
            - The last completed UTC day's data is available 35 minutes after midnight on the next UTC day (00:35), and
              the cache always expires at 00:40 UTC.
            - Works with the coins/{id}/market_chart and coins/{id}/market_chart/range endpoints.
            - Available for public and pro API users.

        """
        price_dfs = []
        market_cap_dfs = []
        total_volume_dfs = []

        # Rate limiting
        rate_limit = 500 if self.pro_api else 10  # 500 req/min for Pro, 10 req/min for others
        delay = 60 / rate_limit  # Calculate delay based on rate limit

        # Handling the days parameter
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'

        for coin_id in tqdm(coin_ids):
            time.sleep(delay)  # Delay the request based on the rate limit
            historical_data = self.coin_historical_market_data(coin_id, vs_currency, days, interval, precision,
                                                               from_date, to_date, timezone_str)

            # Extract each column as a separate DataFrame
            price_df = historical_data[['price']].rename(columns={'price': coin_id})
            market_cap_df = historical_data[['market_cap']].rename(columns={'market_cap': coin_id})
            total_volume_df = historical_data[['total_volume']].rename(columns={'total_volume': coin_id})

            price_dfs.append(price_df)
            market_cap_dfs.append(market_cap_df)
            total_volume_dfs.append(total_volume_df)

        # Combine the individual DataFrames
        combined_price_df = pd.concat(price_dfs, axis=1).dropna()
        combined_market_cap_df = pd.concat(market_cap_dfs, axis=1).dropna()
        combined_total_volume_df = pd.concat(total_volume_dfs, axis=1).dropna()

        return {
            'price': combined_price_df,
            'market_cap': combined_market_cap_df,
            'total_volume': combined_total_volume_df
        }

    def coin_ohlc_data(self, coin_id: str, vs_currency: str = 'usd', days: Union[int, str] = 'max',
                       precision: str = None):
        """Fetch the OHLC (Open, High, Low, Close) data for a given coin from the CoinGecko API and return it as a
        DataFrame.

        This method retrieves OHLC data for a specified cryptocurrency. The granularity of the data is automatic and
        cannot be adjusted for public API users. The granularity varies as follows:

        - 1 to 2 days: 30-minute intervals,
        - 3 to 30 days: 4-hour intervals,
        - 31 days and beyond: 4-day intervals.

        For paid plan users, a 'daily' candle interval parameter is available.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin'). Refers to coins listed by the get_coins_list method.
                Required.
            vs_currency (str, optional): The target currency of market data (e.g., 'usd', 'eur', 'jpy', etc.).
                Default is 'usd'.
            days (Union[int, str], optional): Data up to a number of days ago
                (e.g., '1', '7', '14', '30', '90', '180', '365', 'max'). Default is 'max'.
            precision (str, optional): Decimal precision for currency price value.

        Returns:
            DataFrame: A DataFrame containing the OHLC data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The 'daily' interval is available only for paid plan users for the periods 1/7/14/30/90/180 days.
            - Data is cached and updated every 30 minutes. The last completed UTC day's data is available 35 minutes
              after midnight on the next UTC day (00:35).
            - Works with the coins/{id}/ohlc endpoint.
            - Available for public and pro API users.

        """
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'
        endpoint = f"coins/{coin_id}/ohlc"
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        if precision:
            params['precision'] = precision

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)
        return df

    def multiple_coins_ohlc_data(self, coin_ids: list, vs_currency: str = 'usd', days: Union[int, str] = 'max',
                                 precision: str = None):
        """Fetch the OHLC (Open, High, Low, Close) data for multiple coins and return separate DataFrames for each.

        Note on data granularity for public API users:

        - 1 to 2 days: Data granularity is 30 minutes.
        - 3 to 30 days: Data granularity is 4 hours.
        - 31 days and beyond: Data granularity is 4 days.

        For paid plan users, 'daily' interval can be used by setting the interval parameter.

        Rate Limits:

        - Cache/Update Frequency: Every 30 minutes.
        - The last completed UTC day's data is available 35 minutes after midnight on the next UTC day.

        Args:
            coin_ids (list): List of coin IDs (e.g., ['bitcoin', 'ethereum']). Refers to coins listed using
                get_coins_list method.
            vs_currency (str, optional): The target currency of market data. Default is 'usd'.
            days (Union[int, str], optional): Data up to number of days ago
                (e.g., '1', '7', '14', '30', '90', '180', '365', 'max'). Default is 'max'.
            precision (str, optional): Precision for currency price value.

        Returns:
            dict: A dictionary containing DataFrames for Open, High, Low, Close values for each coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The 'daily' interval is available only for paid plan users for the periods 1/7/14/30/90/180 days.
            - Data is cached and updated every 30 minutes. The last completed UTC day's data is available 35 minutes
              after midnight on the next UTC day (00:35).
            - Works with the coins/{id}/ohlc endpoint.
            - Available for public and pro API users.

        """
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'
        ohlc_data = {'Open': pd.DataFrame(), 'High': pd.DataFrame(), 'Low': pd.DataFrame(), 'Close': pd.DataFrame()}

        # Rate limiting
        rate_limit = 500 if self.pro_api else 10  # 500 req/min for Pro, 10 req/min for others
        delay = 60 / rate_limit  # Calculate delay based on rate limit

        for coin_id in coin_ids:
            time.sleep(delay)  # Delay the request based on the rate limit
            df = self.coin_ohlc_data(coin_id, vs_currency, days, precision)

            for column in ohlc_data:
                ohlc_data[column][coin_id] = df[column]

        return ohlc_data

    # ---------- CONTRACT ---------- #

    def coin_by_contract(self, platform_id: str, contract_address: str) -> dict:
        """
        Fetch coin information using a specific contract address on a given platform.

        Args:
            platform_id (str): ID of the asset platform (e.g., 'ethereum'). Refer to the get_asset_platforms method.
                Required.
            contract_address (str): The contract address of the token. Required.

        Returns:
            dict: A dictionary containing the coin information.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Data is cached and updated every 60 seconds.
            - This endpoint retrieves current data for a coin based on its contract address.
            - Works with the coins/{id}/contract/{contract_address} endpoint.
            - Available for public and pro API users.

        """
        endpoint = f'coins/{platform_id}/contract/{contract_address}'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()
        return response.json()

    def contract_historical_market_data(self, platform_id: str, contract_address: str, vs_currency: str = 'usd',
                                        days: Union[int, str] = 'max', from_date: str = None, to_date: str = None,
                                        precision: str = None, timezone_str: str = 'UTC') -> pd.DataFrame:
        """Fetch historical market data (price, market cap, 24h volume) for a token from its contract address.

        Args:
            platform_id (str): The ID of the platform issuing tokens (e.g., 'ethereum').
            contract_address (str): Token's contract address.
            vs_currency (str, optional): The target currency of market data (e.g., 'usd', 'eur').
            days (Union[int, str], optional): Data up to a number of days ago (e.g., '1', '30', 'max').
            from_date (str, optional): From date in 'mm-dd-yyyy' format or UNIX Timestamp. Optional.
            to_date (str, optional): To date in 'mm-dd-yyyy' format or UNIX Timestamp. Optional.
            precision (str, optional): Decimal precision for currency price value. Defaults to None.
            timezone_str (str, optional): Timezone of the dates. Default is 'UTC'.

        Returns:
            pd.DataFrame: A DataFrame containing historical market data including price, market cap, and 24h volume.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/{id}/contract/{contract_address}/market_chart endpoint.
            - Available for public and pro API users.

        """
        # Convert the dates to UNIX timestamps
        from_timestamp = utils.convert_to_unix(from_date)
        to_timestamp = utils.convert_to_unix(to_date)

        # Handling the days parameter
        days = str(days) if isinstance(days, int) or days == 'max' else 'max'

        if from_timestamp is not None and to_timestamp is not None:
            endpoint = f'coins/{platform_id}/contract/{contract_address}/market_chart/range'
            params = {
                'vs_currency': vs_currency,
                'from': from_timestamp,
                'to': to_timestamp
            }
        else:
            endpoint = f'coins/{platform_id}/contract/{contract_address}/market_chart'
            params = {
                'vs_currency': vs_currency,
                'days': str(days)
            }

        if precision:
            params['precision'] = precision

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        # Splitting the nested lists and converting timestamps
        df = pd.DataFrame(data)
        df['timestamp'] = [ts[0] for ts in df['prices']]
        df['price'] = [price[1] for price in df['prices']]
        df['market_cap'] = [mc[1] for mc in df['market_caps']]
        df['total_volume'] = [vol[1] for vol in df['total_volumes']]

        # Convert UNIX timestamps (in milliseconds) to datetime objects
        tz = pytz.timezone(timezone_str)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['timestamp'] = df['timestamp'].dt.tz_convert(tz)

        # Setting the timestamp as the index and adjusting all timestamps to midnight
        df['timestamp'] = df['timestamp'].apply(lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0))
        df.set_index('timestamp', inplace=True)

        # Dropping the original columns
        df.drop(columns=['prices', 'market_caps', 'total_volumes'], inplace=True)

        return df

    # ---------- ASSET PLATFORMS ---------- #
    def asset_platforms_list(self, platform_filter: str = None):
        """Fetch a list of all asset platforms (blockchain networks) from the CoinGecko API.

        Args:
            platform_filter (str, optional): Apply relevant filters to results.
                Valid values: "nft" for platforms with NFT support. Default is None.

        Returns:
            pd.DataFrame: A DataFrame containing the list of asset platforms.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - The data includes details of various blockchain networks.
            - If the 'filter' is set to "nft", only platforms that support NFTs are returned.
            - Works with the asset_platforms endpoint.
            - Available for public and pro API users.

        """
        endpoint = "asset_platforms"
        params = {}
        if platform_filter:
            params['filter'] = platform_filter

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response
        data = response.json()

        # Convert the JSON response to a DataFrame
        df = pd.DataFrame(data)
        return df

    # ---------- CATEGORIES ---------- #

    def cryptocurrency_categories_list(self) -> pd.DataFrame:
        """Fetches a list of all cryptocurrency categories from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all cryptocurrency categories.
        The data is updated every 5 minutes.

        Returns:
            pd.DataFrame: A DataFrame containing the list of cryptocurrency categories.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/categories/list endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'coins/categories/list'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def categories_market_data(self, order: str = 'market_cap_desc') -> pd.DataFrame:
        """Fetches a list of all cryptocurrency categories with market data from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all cryptocurrency categories,
        including their market data. The data is updated every 5 minutes.

        Args:
            order (str, optional): Ordering of the results. Valid values are 'market_cap_desc' (default),
                'market_cap_asc', 'name_desc', 'name_asc', 'market_cap_change_24h_desc', and
                'market_cap_change_24h_asc'.

        Returns:
            pd.DataFrame: A DataFrame containing the list of cryptocurrency categories with their market data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/categories endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'coins/categories'
        params = {'order': order}
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    # ---------- EXCHANGES ---------- #
    def active_exchanges_list(self, per_page: int = 100, page: int = 1) -> pd.DataFrame:
        """Fetches a list of all active exchanges with trading volumes from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all active exchanges with their trading volumes.
        The data is updated every 60 seconds.

        Args:
            per_page (int, optional): Total results per page. Valid values are from 1 to 250. Defaults to 100.
            page (int, optional): Page number to paginate through results. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all active exchanges with trading volumes.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the exchanges endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'exchanges'
        params = {'per_page': per_page, 'page': page}
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def all_exchanges_list(self) -> pd.DataFrame:
        """Fetches a list of all supported market IDs and names from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all supported markets,
        including their IDs and names. The data is updated every 5 minutes.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all supported markets with their IDs and names.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the exchanges/list endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'exchanges/list'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def exchange_volume_data(self, exchange_id: str = 'gdax') -> pd.DataFrame:
        """Fetches the volume in BTC and top 100 tickers for a specific exchange from the CoinGecko API.

        This method queries the CoinGecko API to retrieve the exchange volume in BTC and information about the top 100
        tickers of a given exchange. For derivatives, a different endpoint is suggested.

        Args:
            exchange_id (str): The ID of the exchange (e.g., 'binance'). Exchange IDs can be obtained from the
                get_supported_exchanges endpoint.

        Returns:
            json: A dictionary containing the exchange volume in BTC and information about the top 100 tickers.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Ticker object is limited to 100 items. For more tickers, use the get_exchange_tickers method.
            - 'is_stale' is true for a ticker not updated from the exchange for more than 8 hours.
            - 'is_anomaly' is true if a ticker's price is an outlier.
            - The user is responsible for managing the display of these information (e.g., footnotes, different
              background, etc.).
            - Works with the exchanges/{id} endpoint.
            - Available for public and pro API users.

        """
        endpoint = f'exchanges/{exchange_id}'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response
        return response.json()

    def exchange_market_tickers(self, exchange_id: str, coin_ids: Optional[str] = None,
                                include_exchange_logo: str = "false", page: int = 1,
                                depth: str = "false", order: str = "trust_score_desc") -> pd.DataFrame:
        """Fetches paginated tickers for a specific exchange from the CoinGecko API.

        This method queries the CoinGecko API to retrieve tickers for a given exchange, with options to filter by coin
        IDs, include exchange logos, specify page number, show 2% orderbook depth, and sort the results.

        Args:
            exchange_id (str): The ID of the exchange (e.g., 'binance'). Exchange IDs can be obtained from
                get_exchange_list method.
            coin_ids (Optional[str], optional): Filter tickers by coin IDs. Defaults to None.
            include_exchange_logo (str, optional): Flag to show exchange logo. Valid values: 'true', 'false'.
                Defaults to 'false'.
            page (int, optional): Page number to paginate through results. Defaults to 1.
            depth (str, optional): Flag to show 2% orderbook depth. Valid values: 'true', 'false'. Defaults to 'false'.
            order (str, optional): Sort order of the results. Valid values: 'trust_score_desc' (default),
                'trust_score_asc', 'volume_desc'.

        Returns:
            pd.DataFrame: A DataFrame containing the exchange tickers with the specified filters and options.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - 'is_stale' is true for a ticker not updated for more than 8 hours.
            - 'is_anomaly' is true if a ticker's price is an outlier.
            - Works with the exchanges/{id}/tickers endpoint.
            - Available for public and pro API users.

        """
        endpoint = f'exchanges/{exchange_id}/tickers'
        params = {
            'coin_ids': coin_ids,
            'include_exchange_logo': include_exchange_logo,
            'page': page,
            'depth': depth,
            'order': order
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data['tickers'])
        return df

    def exchange_historical_volume(self, exchange_id: str = 'gdax', days: Union[int, str] = 30,
                                   from_date: str = None, to_date: str = None) -> pd.DataFrame:
        """
        Fetches either rolling or historical volume data (in BTC) for a given exchange.

        Args:
            exchange_id (str, optional): The ID of the exchange. Defaults to 'gdax'.
            days (Union[int, str], optional): Number of days for the rolling data. Defaults to 30.
            from_date (str, optional): The start date for historical data in 'mm-dd-yyyy' format.
            to_date (str, optional): The end date for historical data in 'mm-dd-yyyy' format.

        Returns:
            pd.DataFrame: A DataFrame containing the volume data of the exchange.

        Raises:
            HTTPError: If the HTTP request fails.
            ValueError: If the date range exceeds 31 days.

        Notes:
            - Works with the exchanges/{id}/volume_chart endpoint.
            - Available for public and pro API users.

        """
        if from_date and to_date:
            # Convert the dates to UNIX timestamps
            from_timestamp = utils.convert_to_unix(from_date)
            to_timestamp = utils.convert_to_unix(to_date)

            if (to_timestamp - from_timestamp) > (31 * 24 * 3600):
                raise ValueError("The date range should not exceed 31 days.")

            endpoint = f'exchanges/{exchange_id}/volume_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            # Rolling volume data
            endpoint = f'exchanges/{exchange_id}/volume_chart'
            params = {'days': days}

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'volume'])
        # Convert timestamps to readable datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        return df.astype(float)

    # ---------- DERIVATIVES ---------- #
    def derivatives_market_tickers(self) -> pd.DataFrame:
        """Fetches a list of all derivative tickers from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all derivative tickers.
        Note: 'open_interest' and 'volume_24h' data are in USD. The data is updated every 30 seconds.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all derivative tickers.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the derivatives/tickers endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'derivatives'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def derivatives_exchanges_list(self, order: str = None, per_page: int = 100, page: int = 1) -> pd.DataFrame:
        """Fetches a list of all derivative exchanges from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all derivative exchanges.
        The data is updated every 60 seconds.

        Args:
            order (str, optional): Order results using params like 'name_asc', 'name_desc',
                                   'open_interest_btc_asc', 'open_interest_btc_desc',
                                   'trade_volume_24h_btc_asc', 'trade_volume_24h_btc_desc'. Defaults to None.
            per_page (int, optional): Total results per page. Defaults to 100.
            page (int, optional): Page number for results pagination. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all derivative exchanges.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the derivatives/exchanges endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'derivatives/exchanges'
        params = {
            'order': order,
            'per_page': per_page,
            'page': page
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def derivatives_exchange_info(self, exchange_id: str = 'binance_futures',
                                  include_tickers: str = None) -> pd.DataFrame:
        """Fetches detailed data for a specific derivative exchange from the CoinGecko API.

        This method queries the CoinGecko API to retrieve detailed data for a given derivative exchange,
        including optional tickers' data. The data is updated every 30 seconds.

        Args:
            exchange_id (str, optional): The ID of the exchange. Exchange IDs can be obtained from
                get_derivatives_exchanges_list method. Defaults to 'binance_futures'.
            include_tickers (str, optional): Option to include tickers data. Valid values are 'all', 'unexpired',
                or leave blank to omit tickers data in the response. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing detailed data for the specified derivative exchange.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the derivatives/exchanges/{id} endpoint.
            - Available for public and pro API users.

        """
        endpoint = f'derivatives/exchanges/{exchange_id}'
        params = {'include_tickers': include_tickers} if include_tickers else {}
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.columns = ['Attribute', 'Value']  # Rename columns for clarity
        return df

    def all_derivatives_exchanges_list(self) -> pd.DataFrame:
        """Fetches a list of all derivative exchanges names and identifiers from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all derivative exchanges,
        including their names and identifiers. The data is updated every 5 minutes.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all derivative exchanges with their names and identifiers.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the derivatives/exchanges/list endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'derivatives/exchanges/list'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    # ---------- NFTs (beta) ---------- #
    def nfts_supported(self, order: str = 'market_cap_usd_desc', asset_platform_id: str = None,
                       per_page: int = 100, page: int = 1) -> pd.DataFrame:
        """Fetches a list of all supported NFT ids from the CoinGecko API, paginated by 100 items per page.

        This method queries the CoinGecko API to retrieve a list of all NFT ids, with options for ordering,
        specifying the asset platform, and paginating the results. The data is updated every 5 minutes.

        Args:
            order (str, optional): Order results by specific fields. Valid values include h24_volume_native_asc/desc,
                floor_price_native_asc/desc, market_cap_native_asc/desc, market_cap_usd_asc/desc. Defaults to None.
            asset_platform_id (str, optional): The id of the platform issuing tokens. See asset_platforms endpoint for
                list of options. Defaults to None.
            per_page (int, optional): Total results per page, valid values from 1 to 250. Defaults to 100.
            page (int, optional): Page number for results pagination. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the list of all NFTs with their ids, contract addresses, names, etc.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the nfts/list endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'nfts/list'
        params = {
            'order': order,
            'asset_platform_id': asset_platform_id,
            'per_page': per_page,
            'page': page
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def nft_collection_info(self, nft_id: str = None,
                            asset_platform_id: str = None,
                            contract_address: str = None) -> pd.DataFrame:
        """Fetches current data for a specific NFT collection from the CoinGecko API.

        This method queries the CoinGecko API to retrieve current data for a given NFT collection,
        identified either by its ID or by its asset platform ID and contract address.
        The data is updated every 60 seconds.

        Args:
            nft_id (str, optional): The ID of the NFT collection. Can be obtained from get_supported_nfts method.
            asset_platform_id (str, optional): The ID of the platform issuing tokens. See the asset_platforms endpoint
                for options.
            contract_address (str, optional): The contract address of the NFT collection. Can be obtained from
                get_supported_nfts method.

        Returns:
            pd.DataFrame: A DataFrame containing current data for the specified NFT collection.

        Raises:
            ValueError: If neither nft_id nor both asset_platform_id and contract_address are provided.
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the nfts/{id} and nfts/{asset_platform_id}/contract/{contract_address}.
            - Available for public and pro API users.

        Raises:
            ValueError: If neither nft_id nor both asset_platform_id and contract_address are provided.

        """
        if nft_id:
            endpoint = f'nfts/{nft_id}'
        elif asset_platform_id and contract_address:
            endpoint = f'nfts/{asset_platform_id}/contract/{contract_address}'
        else:
            raise ValueError("Either nft_id or both asset_platform_id and contract_address must be provided")

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame([data])
        df.set_index('id', inplace=True)  # Set 'id' as the index
        return df

    def nft_collections_info(self, nft_ids: list = None,
                             asset_platform_id: str = None,
                             contract_addresses: list = None) -> pd.DataFrame:
        """Fetches current data for multiple NFT collections from the CoinGecko API.

        This method queries the CoinGecko API to retrieve current data for multiple NFT collections,
        identified either by a list of their IDs or by a combination of an asset platform ID and a list of
        contract addresses. The data is updated every 60 seconds.

        Args:
            nft_ids (list, optional): A list of NFT collection IDs.
            asset_platform_id (str, optional): The ID of the platform issuing tokens. See the asset_platforms endpoint.
            contract_addresses (list, optional): A list of contract addresses of NFT collections.

        Returns:
            pd.DataFrame: A DataFrame containing current data for the specified NFT collections.

        Raises:
            HTTPError: If the HTTP request fails.
            ValueError: If neither nft_ids nor both asset_platform_id and contract_addresses are provided.

        Notes:
            - Works with the nfts/{id} endpoint.
            - Also works with nfts/{asset_platform_id}/contract/{contract_address} endpoint.
            - Available for public and pro API users.

        Raises:
            ValueError: If neither nft_ids nor both asset_platform_id and contract_addresses are provided.

        """
        if nft_ids:
            collections_data = [self.nft_collection_info(nft_id=nft_id) for nft_id in nft_ids]
        elif asset_platform_id and contract_addresses:
            collections_data = [self.nft_collection_info(asset_platform_id=asset_platform_id, contract_address=address)
                                for address in contract_addresses]
        else:
            raise ValueError("Either 'nft_ids' must be provided or both 'asset_platform_id' and 'contract_addresses'.")

        # Filter out empty or all-NA DataFrames
        valid_collections_data = [df.dropna(how='all', axis=1) for df in collections_data if not df.empty]

        # Combine all valid DataFrames into one, if any valid data exists
        if valid_collections_data:
            combined_df = pd.concat(valid_collections_data, ignore_index=True)
        else:
            combined_df = pd.DataFrame()

        return combined_df

    # ---------- EXCHANGE RATES ---------- #
    def btc_exchange_rates(self) -> pd.DataFrame:
        """Fetches BTC-to-Currency exchange rates from the CoinGecko API.

        This method queries the CoinGecko API to retrieve BTC-to-Currency exchange rates.
        The data is updated every 60 seconds.

        Returns:
            pd.DataFrame: A DataFrame containing the BTC-to-Currency exchange rates.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the exchange_rates endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'exchange_rates'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json().get('rates', {})
        df = pd.DataFrame.from_dict(data, orient='index')
        return df

    # ---------- SEARCH ---------- #
    def search_coingecko(self, query: str) -> dict:
        """Searches for coins, categories, and markets on CoinGecko.

        This method queries the CoinGecko API to search for coins, categories, and markets listed on CoinGecko,
        ordered by largest Market Cap first. The data is updated every 15 minutes.

        Args:
            query (str): The search string.

        Returns:
            dict: A dictionary containing the search results as DataFrames.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the search endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'search'
        params = {'query': query}
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrames and store in dictionary
        dfs = {}
        data = response.json()
        for key, value in data.items():
            dfs[key] = pd.DataFrame(value)
        return dfs

    # ---------- TRENDING ---------- #
    def trending_searches(self) -> pd.DataFrame:
        """Fetches the top-7 trending search coins on CoinGecko in the last 24 hours.

        This method queries the CoinGecko API to retrieve the top-7 trending coins as searched by users
        in the last 24 hours, ordered by most popular first. The data is updated every 10 minutes.

        Returns:
            pd.DataFrame: A DataFrame containing the list of top-7 trending coins, ordered by most popular first.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the search/trending endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'search/trending'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json().get('coins', [])
        # Flatten the data and create a DataFrame
        trending_coins = [coin['item'] for coin in
                          data]  # Assuming each coin's data is in a sub-dictionary under 'item'
        df = pd.DataFrame(trending_coins)
        return df

    # ---------- GLOBAL ---------- #
    def global_crypto_stats(self) -> Tuple:
        """Fetches global cryptocurrency data from the CoinGecko API.

        This method queries the CoinGecko API to retrieve global cryptocurrency data,
        including total volume, total market cap, ongoing ICOs, and other relevant details.
        The data is updated every 10 minutes.

        Returns:
            Tuple: A DataFrame containing global cryptocurrency data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the global endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'global'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        # The data structure here is assumed to be a dictionary. Adjust the DataFrame creation as necessary.
        df = pd.DataFrame(data)
        market_cap_percentage = pd.DataFrame.from_dict(
            df.loc['market_cap_percentage', 'data'], orient='index', columns=['market_cap_percentage']
        )
        total_market_cap = pd.DataFrame.from_dict(
            df.loc['total_market_cap', 'data'], orient='index', columns=['total_market_cap']
        )
        total_volume = pd.DataFrame.from_dict(
            df.loc['total_volume', 'data'], orient='index', columns=['total_volume']
        )
        return df, market_cap_percentage, total_market_cap, total_volume

    def global_defi_stats(self) -> pd.DataFrame:
        """Fetches global decentralized finance (DeFi) data from the CoinGecko API.

        This method queries the CoinGecko API to retrieve global DeFi data, including market capitalization in USD,
        Ethereum market capitalization, DeFi to Ethereum ratio, 24-hour trading volume, DeFi dominance,
        and the top DeFi coin's name and dominance. The data is updated every 60 minutes.

        Returns:
            pd.DataFrame: A DataFrame containing global DeFi data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the global/decentralized_finance_defi endpoint.
            - Available for public and pro API users.

        """
        endpoint = 'global/decentralized_finance_defi'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        # Since the data is likely a single dictionary, create a DataFrame with a single row
        df = pd.DataFrame(data)
        return df

    # ---------- COMPANIES (beta) ---------- #
    def companies_holdings(self, coin_id: str = 'bitcoin') -> pd.DataFrame:
        """Fetches data on public companies' Bitcoin or Ethereum holdings from the CoinGecko API.

        This method queries the CoinGecko API to retrieve data about public companies' holdings of Bitcoin or
        Ethereum, ordered by total holdings in descending order.

        Args:
            coin_id (str): The coin identifier ('bitcoin' or 'ethereum').

        Returns:
            pd.DataFrame: A DataFrame containing data on public companies' Bitcoin or Ethereum holdings.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the companies/public_treasury/{coin_id} endpoint.
            - Available for public and pro API users.

        """
        endpoint = f'companies/public_treasury/{coin_id}'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json().get('companies', [])
        df = pd.DataFrame(data)
        return df

    # ---------- PAID PLAN ENDPOINTS ---------- #
    def new_coins_listed(self) -> pd.DataFrame:
        """Fetches the latest 200 coins recently listed on CoinGecko.

        This method queries the CoinGecko API to retrieve the latest 200 coins that were recently listed on
        CoinGecko.com, along with their IDs, symbols, names, and activation times. The data is updated every 30 seconds.

        Note: Access to this endpoint requires a paid plan (e.g., Analyst, Lite, Pro, Enterprise).

        Returns:
            pd.DataFrame: A DataFrame containing the latest 200 coins listed on CoinGecko.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/listed/new endpoint.
            - Available for pro and enterprise API users only.

        """
        endpoint = 'coins/list/new'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def gainers_losers(self, vs_currency: str = 'usd', duration: str = '24h',
                       top_coins: int = 1000) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetches the top 30 coins with the largest price gains and losses for a specific duration.

        This method queries the CoinGecko API to retrieve the top 30 coins with the largest price gains and
        losses by a specific time duration. The data is updated every 5 minutes.

        Note: Access to this endpoint requires a paid plan (e.g., Analyst, Lite, Pro, Enterprise).

        Args:
            vs_currency (str, optional): The target currency for market data. Default is 'usd'.
            duration (str, optional): The time duration for the price change (e.g., '1h', '24h'). Options include: '1h',
                '24h', '7d', '14d', '30d', '60d', '1y'. Default is '24h'.
            top_coins (int, optional): The number of top coins to include. Default is 1000.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple of DataFrames containing the top gainers and losers.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/top_gainers_losers endpoint.
            - Available for pro and enterprise API users only.

        """
        endpoint = 'coins/top_gainers_losers'
        params = {
            'vs_currency': vs_currency,
            'duration': duration,
            'top_coins': top_coins
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        gainers = pd.DataFrame(data['top_gainers'])
        losers = pd.DataFrame(data['top_losers'])
        return gainers, losers

    def historical_global_market_cap(self, days: Union[int, str] = 'max', vs_currency: str = 'usd') -> tuple:
        """Fetches historical global market cap and volume data from the CoinGecko API.

        This method queries the CoinGecko API to retrieve historical global market cap and volume data, based on the
        specified number of days from now.

        Args:
            days (Union[int, str], optional): Number of days from now for the historical data. Defaults to 'max'.
            vs_currency (str, optional): The target currency for market data. Defaults to 'usd'.

        Returns:
            tuple: A tuple of DataFrames containing historical global market cap and volume data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the global/market_cap_chart endpoint.
            - Available for pro and enterprise API users only.

        """
        endpoint = 'global/market_cap_chart'
        params = {
            'days': days,
            'vs_currency': vs_currency
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()

        # Convert the JSON response to separate DataFrames for market cap and volume
        data = response.json()['market_cap_chart']
        market_cap_data = data['market_cap']
        volume_data = data['volume']

        # Create DataFrames
        market_cap_df = pd.DataFrame(market_cap_data, columns=['timestamp', 'market_cap'])
        volume_df = pd.DataFrame(volume_data, columns=['timestamp', 'volume'])

        # Convert timestamps to readable datetime format
        market_cap_df['timestamp'] = pd.to_datetime(market_cap_df['timestamp'], unit='ms')
        volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')

        # Set the timestamp as the index
        market_cap_df.set_index('timestamp', inplace=True)
        volume_df.set_index('timestamp', inplace=True)

        return market_cap_df, volume_df

    def nft_market_data(self, asset_platform_id: str = None, order: str = None, per_page: int = 100,
                        page: int = 1) -> pd.DataFrame:
        """Fetches a list of supported NFTs with market data from the CoinGecko API.

        This method queries the CoinGecko API to retrieve a list of all supported NFTs, including floor price,
        market cap, volume, and other market-related data. The data is updated every 5 minutes.

        Note: Access to this endpoint requires a paid plan (e.g., Analyst, Lite, Pro, Enterprise).

        Args:
            asset_platform_id (str, optional): The id of the platform issuing tokens. Defaults to None.
            order (str, optional): Order results using parameters like 'h24_volume_native_desc'. Defaults to None.
            per_page (int, optional): Total results per page. Defaults to 100.
            page (int, optional): Page number to paginate through results. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the list of supported NFTs with market data.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the nfts/markets endpoint.
            - Available for pro and enterprise API users only.

        """
        endpoint = 'nfts/markets'
        params = {
            'asset_platform_id': asset_platform_id,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        return df

    def nft_historical_data(self, nft_id: str = None, asset_platform_id: str = None,
                            contract_address: str = None, days: Union[int, str] = 'max') -> pd.DataFrame:
        """
        Fetches historical market data of a specific NFT collection from the CoinGecko API using either the
        NFT ID or the asset platform ID and contract address.

        Args:
            nft_id (str, optional): The ID of the NFT collection. Defaults to None.
            asset_platform_id (str, optional): The ID of the asset platform (e.g., 'ethereum'). Defaults to None.
            contract_address (str, optional): The contract address of the NFT collection. Defaults to None.
            days (Union[int, str]): Number of days from now for the historical data. Defaults to 'max'.

        Returns:
            pd.DataFrame: A DataFrame containing historical market data for the specified NFT collection.

        Raises:
            ValueError: If neither nft_id nor both asset_platform_id and contract_address are provided.
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the nfts/{id}/market_chart and
                nfts/{asset_platform_id}/contract/{contract_address}/market_chart endpoints.
            - Available for pro and enterprise API users only.

        """
        if nft_id:
            endpoint = f'nfts/{nft_id}/market_chart'
        elif asset_platform_id and contract_address:
            endpoint = f'nfts/{asset_platform_id}/contract/{contract_address}/market_chart'
        else:
            raise ValueError("Must provide either 'nft_id' or both 'asset_platform_id' and 'contract_address'")

        params = {'days': days}
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()

        # Extract data series
        data = response.json()
        series_names = ['floor_price_usd', 'floor_price_native', 'h24_volume_usd', 'h24_volume_native',
                        'market_cap_usd', 'market_cap_native']

        # Create DataFrames for each series and merge them
        dfs = []
        for series_name in series_names:
            series_data = data.get(series_name, [])
            if series_data:
                temp_df = pd.DataFrame(series_data, columns=['timestamp', series_name])
                temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'], unit='ms')
                temp_df.set_index('timestamp', inplace=True)
                dfs.append(temp_df)

        # Merge all series DataFrames
        final_df = pd.concat(dfs, axis=1)
        return final_df

    def nft_market_tickers(self, nft_id: str) -> pd.DataFrame:
        """Fetches the latest floor price and 24h volume of an NFT collection on each NFT marketplace.

        This method queries the CoinGecko API to retrieve the latest floor price and 24-hour volume data for a
        specific NFT collection, as listed on various NFT marketplaces.

        Note: Access to this endpoint requires a paid plan (e.g., Analyst, Lite, Pro, Enterprise).

        Args:
            nft_id (str): The ID of the NFT collection.

        Returns:
            pd.DataFrame: A DataFrame containing the floor price and 24h volume data of the NFT collection on different
            marketplaces.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the nfts/{id}/tickers endpoint.
            - Available for pro and enterprise API users only.

        """
        endpoint = f'nfts/{nft_id}/tickers'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        tickers_data = data.get('tickers', [])
        df = pd.DataFrame(tickers_data)
        return df

    # ---------- ENTERPRISE PLAN ENDPOINTS ---------- #
    def coin_circulating_supply_history(self, coin_id: str = 'bitcoin', days: int = 'max',
                                        interval: str = 'daily', from_date: str = None,
                                        to_date: str = None) -> pd.DataFrame:
        """
        Fetches historical circulating supply data for a coin, either for a specified number of days or within a date
        range.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin').
            days (int): Number of days from now for the historical data. Can be up to 'max' available days.
            interval (str): Data interval. Valid values include 'daily', 'hourly', and '5-minutely'.
            from_date (str, optional): Start date in 'mm-dd-yyyy' format for date range query.
            to_date (str, optional): End date in 'mm-dd-yyyy' format for date range query.

        Returns:
            pd.DataFrame: A DataFrame containing the circulating supply data of the specified coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/{id}/circulating_supply_chart endpoint.
            - Available for pro and enterprise API users only.

        """
        if from_date and to_date:
            # Historical data within a specified date range
            from_timestamp = utils.convert_to_unix(from_date)
            to_timestamp = utils.convert_to_unix(to_date)
            endpoint = f'coins/{coin_id}/circulating_supply_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            # Historical data for specified number of days
            endpoint = f'coins/{coin_id}/circulating_supply_chart'
            params = {'days': days, 'interval': interval}

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data['circulating_supply'], columns=['timestamp', 'circulating_supply'])
        # Convert timestamps to readable datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def coin_total_supply_history(self, coin_id: str, days: int = 30, interval: str = 'daily',
                                  from_date: str = None, to_date: str = None) -> pd.DataFrame:
        """
        Fetches historical total supply data for a coin, either for a specified number of days or within a date range.

        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin').
            days (int): Number of days from now for the historical data. Can be up to 'max' available days.
            interval (str): Data interval. Valid values include 'daily', 'hourly', and '5-minutely'.
            from_date (str, optional): Start date in 'mm-dd-yyyy' format for date range query.
            to_date (str, optional): End date in 'mm-dd-yyyy' format for date range query.

        Returns:
            pd.DataFrame: A DataFrame containing the total supply data of the specified coin.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the coins/{id}/total_supply_chart
            - Also works with the coins/{coin_id}/total_supply_chart/range endpoints.
            - Available for pro and enterprise API users only.

        """
        if from_date and to_date:
            # Convert the dates to UNIX timestamps
            from_timestamp = utils.convert_to_unix(from_date)
            to_timestamp = utils.convert_to_unix(to_date)
            endpoint = f'coins/{coin_id}/total_supply_chart/range'
            params = {'from': from_timestamp, 'to': to_timestamp}
        else:
            # Historical data for specified number of days
            endpoint = f'coins/{coin_id}/total_supply_chart'
            params = {'days': days, 'interval': interval}

        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint, params=params)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        df = pd.DataFrame(data['total_supply'], columns=['timestamp', 'total_supply'])
        # Convert timestamps to readable datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def all_tokens_list(self, asset_platform_id: str) -> pd.DataFrame:
        """Retrieves a full list of tokens for a specific blockchain network supported by Ethereum token list standard.

        Args:
            asset_platform_id (str): The ID of the blockchain network (e.g., 'ethereum', 'polygon-pos').

        Returns:
            pd.DataFrame: A DataFrame containing a comprehensive list of tokens for the specified blockchain network.

        Raises:
            HTTPError: If the HTTP request fails.

        Notes:
            - Works with the token_lists/{asset_platform_id}/all endpoint.
            - Use get_asset_platforms method to retrieve a list of supported blockchain networks.
            - Available for enterprise API users only.

        """
        endpoint = f'token_lists/{asset_platform_id}/all.json'
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()  # Ensure a successful response

        # Convert the JSON response to a DataFrame
        data = response.json()
        tokens = data.get('tokens', [])
        df = pd.DataFrame(tokens)
        return df
