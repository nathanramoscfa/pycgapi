import pandas as pd

from .base import CoinGeckoAPI


class Trending(CoinGeckoAPI):
    def trending_searches(self) -> pd.DataFrame:
        """
        Fetches the top trending search items on CoinGecko in the last 24 hours,
        including trending coins, NFTs, and categories based on user searches
        and changes in floor prices.

        Returns:
            pd.DataFrame: Contains data for the top trending items, ordered by
                popularity, with details such as name, symbol, and market rank
                for coins.

        Notes:
            - Endpoint: 'search/trending'.
            - Data updates every 10 minutes.
            - Returns information for:
              * Top 15 trending coins
              * Top 7 trending NFTs
              * Top 5 trending categories
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/trending-search

        """
        endpoint = 'search/trending'
        response = self._get(endpoint)
        data = response.get('coins', [])
        trending_coins = [coin['item'] for coin in data]
        return pd.DataFrame(trending_coins).set_index('id')
