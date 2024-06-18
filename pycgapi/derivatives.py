import pandas as pd

from .base import CoinGeckoAPI


class Derivatives(CoinGeckoAPI):
    def derivatives_market_tickers(self) -> pd.DataFrame:
        """
        Fetches a comprehensive list of derivative tickers from the
        CoinGecko API, including open interest and 24-hour volume.

        Returns:
            pd.DataFrame: Contains derivative tickers with data fields
                such as market name, price, open interest, and 24h volume.

        Notes:
            - Endpoint: 'derivatives'.
            - Includes fields like 'open_interest' and 'volume_24h', in USD.
            - Data updates every 30 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/derivatives-tickers

        """
        endpoint = 'derivatives/tickers'
        response = self._get(endpoint)
        return pd.DataFrame(response)

    def derivatives_exchanges_list(
        self,
        order: str = None,
        per_page: int = 100,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches a list of all derivative exchanges from the CoinGecko API,
        with optional sorting and pagination.

        Args:
            order (str, optional): Sort results by fields like 'name_asc',
                'name_desc', or 'open_interest_btc_desc'. Defaults to None.
            per_page (int, optional): Number of results per page.
                Defaults to 100.
            page (int, optional): Page number for results pagination.
                Defaults to 1.

        Returns:
            pd.DataFrame: Contains detailed data about each derivative exchange,
                including id, name, open interest, and trading volume.

        Notes:
            - Endpoint: 'derivatives/exchanges'.
            - Data updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/derivatives-exchanges

        """
        endpoint = 'derivatives/exchanges'
        params = {
            'order': order,
            'per_page': per_page,
            'page': page
        }
        response = self._get(endpoint, **params)
        return pd.DataFrame(response)

    def derivatives_exchange_info(
        self,
        exchange_id: str = 'binance_futures',
        include_tickers: str = None
    ) -> pd.DataFrame:
        """
        Fetches detailed information for a specified derivatives exchange,
        including optional tickers data.

        Args:
            exchange_id (str, optional): ID of the exchange. Defaults to
                'binance_futures'. Obtainable from
                get_derivatives_exchanges_list.
            include_tickers (str, optional): If specified, includes tickers
                data. Options are 'all', 'unexpired', or None for no tickers.

        Returns:
            pd.DataFrame: DataFrame with detailed attributes of the exchange,
                such as ID, name, and open interest, formatted as 'Attribute'
                and 'Value'.

        Notes:
            - Endpoint: 'derivatives/exchanges/{id}'.
            - Updates every 30 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/derivatives-exchanges-id

        """
        endpoint = f'derivatives/exchanges/{exchange_id}'
        params = {'include_tickers': include_tickers} if include_tickers else {}
        response = self._get(endpoint, **params)
        df = pd.DataFrame.from_dict(response, orient='index').reset_index()
        df.columns = ['Attribute', 'Value']
        return df

    def all_derivatives_exchanges_list(self) -> pd.DataFrame:
        """
        Retrieves a comprehensive list of all derivatives exchanges
        from the CoinGecko API, including each exchange's name and id.

        Returns:
            pd.DataFrame: Contains the names and identifiers of all
                derivative exchanges listed on CoinGecko.

        Notes:
            - Endpoint: 'derivatives/exchanges/list'.
            - Data updates every 5 minutes.
            - API Documentation:
              https://docs.coingecko.com/reference/derivatives-exchanges-list

        """
        endpoint = 'derivatives/exchanges/list'
        response = self._get(endpoint)
        return pd.DataFrame(response)
