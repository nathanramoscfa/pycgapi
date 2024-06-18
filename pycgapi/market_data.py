import math
import time

import pandas as pd
from typing import Tuple

from .base import CoinGeckoAPI


class MarketData(CoinGeckoAPI):
    def coins_list(self, include_platform: bool = False) -> pd.DataFrame:
        """
        Fetches a list of all supported active coins from CoinGecko,
        including their ID, name, and symbol. Optionally includes platform
        contract addresses.

        Args:
            include_platform (bool, optional): If True, includes the
                platform contract addresses for tokens (e.g., Ethereum).
                Defaults to False.

        Returns:
            pd.DataFrame: Contains ID, name, and symbol of each coin.
                Includes platform contract addresses if 'include_platform'
                is True.

        Notes:
            - Endpoint: 'coins/list'.
            - Retrieves only active coins; inactive or deactivated coins
              are excluded.
            - Data is updated every 5 minutes.
            - No pagination is needed for this endpoint.
            - API Documentation:
              https://docs.coingecko.com/reference/coins-list

        """
        endpoint = 'coins/list'
        params = {'include_platform': 'true' if include_platform else 'false'}
        response = self._get(endpoint, **params)
        df = pd.DataFrame(response)
        df.set_index('id', inplace=True)
        return df

    def coins_market_data(
        self,
        vs_currency: str = 'usd',
        ids: str = None,
        category: str = None,
        order: str = "market_cap_desc",
        per_page: int = 100,
        page: int = 1,
        sparkline: bool = False,
        price_change_percentage: str = None,
        locale: str = "en",
        precision: str = None
    ) -> pd.DataFrame:
        """
        Retrieves market data for coins including price, market cap, volume,
        and more from CoinGecko. Data is updated every 45 seconds.

        Args:
            vs_currency (str, optional): Currency for market data. Defaults
                to 'usd'.
            ids (str, optional): Comma-separated coin identifiers. Refer to
                get_coins_list method.
            category (str, optional): Filter by coin category. See
                get_coin_categories.
            order (str, optional): Order of results. Defaults to
                "market_cap_desc".
            per_page (int, optional): Results per page (1 to 250). Defaults
                to 100.
            page (int, optional): Page number for results. Defaults to 1.
            sparkline (bool, optional): Include 7-day sparkline data. Defaults
                to False.
            price_change_percentage (str, optional): Comma-separated list of
                timeframes for price change data (e.g., '1h', '24h', '7d').
            locale (str, optional): Locale for market data formatting. Defaults
                to 'en'.
            precision (str, optional): Decimal precision for price values.

        Returns:
            pd.DataFrame: Contains comprehensive market data for specified
                coins, formatted as requested.

        Notes:
            - Endpoint: 'coins/markets'.
            - Category takes precedence over ids if both are provided.
            - API Documentation:
              https://docs.coingecko.com/reference/coins-markets

        """
        endpoint = 'coins/markets'
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
        response = self._get(endpoint, **params)
        df = pd.DataFrame(response)
        df.set_index('id', inplace=True)
        return df

    def top_coins_market_data(self, top_n: int = 250) -> pd.DataFrame:
        """
        Fetches market data for the top N cryptocurrencies by market cap
        from CoinGecko, efficiently handling API pagination.

        Args:
            top_n (int, optional): The number of top cryptocurrencies to fetch.
                Defaults to 250, the maximum allowed per page by the API.

        Returns:
            pd.DataFrame: Contains market data of the top N cryptocurrencies,
                sorted by market cap. Data includes price, volume, and other
                related market statistics.

        Notes:
            - Endpoint: 'coins/markets'.
            - Paginates through the API to gather data on the top N coins,
              managing request frequency based on user's API rate limits.
            - Be mindful of API rate limits; adjust delay in request as
              necessary.
            - API Documentation:
              https://docs.coingecko.com/reference/coins-markets

        """
        per_page = 250  # Max items per page allowed by the API
        total_pages = math.ceil(top_n / per_page)
        all_coins_df = pd.DataFrame()

        # Rate limiting adjustments
        rate_limit = 500 if self.pro_api else 10  # API rate limit
        delay = 60 / rate_limit  # Calculate delay based on rate limit

        for page in range(1, total_pages + 1):
            time.sleep(delay)  # Respect the rate limit
            page_df = self.coins_market_data(vs_currency='usd',
                                             per_page=per_page, page=page)
            all_coins_df = pd.concat([all_coins_df, page_df],
                                     ignore_index=True)
            if len(all_coins_df) >= top_n:
                break  # Stop fetching more pages if the top N already fetched

        return all_coins_df.iloc[:top_n]  # Ensure only top N rows are returned

    def coin_info(
        self,
        coin_id: str,
        localization: str = 'true',
        tickers: bool = True,
        market_data: bool = True,
        community_data: bool = True,
        developer_data: bool = True,
        sparkline: bool = False
    ) -> dict:
        """
        Retrieves comprehensive data for a specified coin from CoinGecko,
        including market data, community stats, developer stats, and more.

        Args:
            coin_id (str): ID of the coin (e.g., 'bitcoin'). Refer to
                'get_coins_list' for valid IDs.
            localization (str, optional): If 'true', includes all localized
                languages in the response. Defaults to 'true'.
            tickers (bool, optional): If True, includes ticker data.
                Defaults to True.
            market_data (bool, optional): If True, includes market data.
                Defaults to True.
            community_data (bool, optional): If True, includes community
                data such as Twitter followers and Telegram channel size.
                Defaults to True.
            developer_data (bool, optional): If True, includes developer
                data such as Github forks, stars, and pull requests.
                Defaults to True.
            sparkline (bool, optional): If True, includes sparkline data
                for the last 7 days. Defaults to False.

        Returns:
            dict: Contains detailed data for the coin, including name,
            price, market cap, community info, developer stats, etc.

        Notes:
            - Endpoint: 'coins/{id}'.
            - Ticker data is limited to 100 items; for more,
              visit 'coins/{id}/tickers'.
            - Community data updated weekly.
            - API Documentation:
              https://docs.coingecko.com/reference/coins-id
            - For more detailed coin identifiers, refer to the Google Sheets:
              https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?usp=sharing

        """
        endpoint = f'coins/{coin_id}'
        params = {
            'localization': localization,
            'tickers': tickers,
            'market_data': market_data,
            'community_data': community_data,
            'developer_data': developer_data,
            'sparkline': sparkline
        }
        response = self._get(endpoint, **params)
        return response

    def new_coins_listed(self) -> pd.DataFrame:
        """
        Fetches the latest 200 coins recently listed on CoinGecko,
        providing their IDs, symbols, names, and activation times.

        Returns:
            pd.DataFrame: Contains the IDs, symbols, names, and
                activation times of the latest 200 coins listed on
                CoinGecko.

        Notes:
            - Endpoint: 'coins/list/new'.
            - Retrieves data for the newest 200 listings updated every
              30 seconds.
            - Exclusive for Paid Plan Subscribers (Analyst, Lite, Pro,
              and Enterprise).
            - CoinGecko equivalent page:
              https://www.coingecko.com/en/new-cryptocurrencies
            - API Documentation:
              https://docs.coingecko.com/reference/coins-list-new

        """
        endpoint = 'coins/list/new'
        response = self._get(endpoint)
        return pd.DataFrame(response)

    def gainers_losers(
        self,
        vs_currency: str = 'usd',
        duration: str = '24h',
        top_coins: int = 1000
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetches the top 30 coins with the largest price gains and losses
        over a specified duration, considering trading volume limits.

        Args:
            vs_currency (str, optional): Currency for market data. Defaults
                to 'usd'. Supported currencies can be found at
                /simple/supported_vs_currencies.
            duration (str, optional): Time duration for price change,
                options include '1h', '24h', '7d', '14d', '30d', '60d', '1y'.
                Defaults to '24h'.
            top_coins (int, optional): Number of top coins to consider based
                on market cap ranking. Valid values: 300, 500, 1000, or 'all'.
                Defaults to 1000.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: First DataFrame contains top
                gainers, second contains top losers, each filtered by the
                specified criteria.

        Notes:
            - Endpoint: 'coins/top_gainers_losers'.
            - Only includes coins with a minimum 24-hour trading volume of
              $50,000.
            - Data updates every 5 minutes.
            - Exclusive to Paid Plan Subscribers (Analyst, Lite, Pro,
              Enterprise).
            - API Documentation:
              https://docs.coingecko.com/reference/coins-top-gainers-losers
            - CoinGecko equivalent page:
              https://www.coingecko.com/en/crypto-gainers-losers

        """
        endpoint = 'coins/top_gainers_losers'
        params = {
            'vs_currency': vs_currency,
            'duration': duration,
            'top_coins': top_coins
        }
        response = self._get(endpoint, **params)
        gainers = pd.DataFrame(response['top_gainers'])
        losers = pd.DataFrame(response['top_losers'])
        return gainers, losers
