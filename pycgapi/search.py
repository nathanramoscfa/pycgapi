import pandas as pd

from .base import CoinGeckoAPI


class Search(CoinGeckoAPI):
    def search_coingecko(self, query: str) -> dict:
        """
        Searches for coins, categories, and markets on CoinGecko based on
        a provided query string. Returns the results organized by type.

        Args:
            query (str): The search string used to query CoinGecko.

        Returns:
            dict: Search results, with each category such as coins, categories,
                and markets returned as a separate DataFrame.

        Notes:
            - Endpoint: 'search'.
            - Results include various entities sorted by relevance and market
              cap in descending order.
            - Data refreshes every 15 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/search-data

        """
        endpoint = 'search'
        params = {'query': query}
        response = self._get(endpoint, **params)
        dfs = {}
        for key, value in response.items():
            dfs[key] = pd.DataFrame(value)
        return dfs
