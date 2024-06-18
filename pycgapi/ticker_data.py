import pandas as pd

from .base import CoinGeckoAPI


class TickerData(CoinGeckoAPI):
    def coin_market_tickers(
        self,
        coin_id: str,
        exchange_ids: str = None,
        include_exchange_logo: bool = False,
        page: int = 1,
        order: str = 'trust_score_desc',
        depth: bool = False
    ) -> pd.DataFrame:
        """
        Retrieves ticker information for a specified cryptocurrency, including
        price, volume, and last trading time from various exchanges.

        Args:
            coin_id (str): The coin's ID (e.g., 'bitcoin'). Refer to
                '/coins/list' for valid IDs.
            exchange_ids (str, optional): Comma-separated exchange IDs to filter
                results (e.g., 'binance,kraken'). Defaults to None.
            include_exchange_logo (bool, optional): If True, includes exchange
                logos in the results. Defaults to False.
            page (int, optional): Page number for pagination. Defaults to 1.
            order (str, optional): Order of ticker results, e.g.,
                'trust_score_desc'. Defaults to 'trust_score_desc'.
            depth (bool, optional): If True, includes 2% orderbook depth data.
                Defaults to False.

        Returns:
            pd.DataFrame: Contains ticker data for the specified coin
                across various exchanges, detailed with exchange, price, and
                volume.

        Notes:
            - Endpoint: 'coins/{id}/tickers'.
            - Data is updated every 2 minutes.
            - Pagination is supported, with up to 100 items per page.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-tickers

        """
        endpoint = f'coins/{coin_id}/tickers'
        params = {
            'exchange_ids': exchange_ids,
            'include_exchange_logo': include_exchange_logo,
            'page': page,
            'order': order,
            'depth': depth
        }
        response = self._get(endpoint, **params)
        return pd.DataFrame(response['tickers'])
