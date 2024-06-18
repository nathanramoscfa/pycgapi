import pandas as pd

from .base import CoinGeckoAPI


class Categories(CoinGeckoAPI):
    def cryptocurrency_categories_list(self) -> pd.DataFrame:
        """
        Retrieves a list of all cryptocurrency categories from CoinGecko.

        Returns:
            pd.DataFrame: Includes category IDs and names.

        Notes:
            - Endpoint: coins/categories/list
            - Data updated every 5 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-categories-list

        """
        endpoint = 'coins/categories/list'
        response = self._get(endpoint)
        return pd.DataFrame(response)

    def categories_market_data(
        self,
        order: str = 'market_cap_desc'
    ) -> pd.DataFrame:
        """
        Fetches market data for cryptocurrency categories from CoinGecko,
        including market cap and volume.

        Args:
            order (str, optional): Ordering of results. Valid options are:
                'market_cap_desc', 'market_cap_asc', 'name_asc', 'name_desc',
                'market_cap_change_24h_desc', 'market_cap_change_24h_asc'

        Returns:
            pd.DataFrame: Contains categories and their market data.

        Notes:
            - Endpoint: coins/categories
            - Data updates every 5 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-categories

        """
        endpoint = 'coins/categories'
        params = {'order': order}
        response = self._get(endpoint, **params)
        return pd.DataFrame(response)
