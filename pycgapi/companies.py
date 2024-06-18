import pandas as pd

from .base import CoinGeckoAPI


class Companies(CoinGeckoAPI):
    def companies_holdings(self, coin_id: str = 'bitcoin') -> pd.DataFrame:
        """
        Fetches data on public companies' holdings of specified cryptocurrencies
        (default is Bitcoin) from CoinGecko.

        Args:
            coin_id (str, optional): Cryptocurrency identifier ('bitcoin' or
                'ethereum'). Default is 'bitcoin'.

        Returns:
            pd.DataFrame: Contains public companies' holdings, including amount
                held and value in USD.

        Notes:
            - Endpoint: companies/public_treasury/{coin_id}
            - Data sorted by total holdings in descending order.
            - Data is updated frequently for all API users.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/companies-public-treasury

        """
        endpoint = f'companies/public_treasury/{coin_id}'
        response = self._get(endpoint)
        return pd.DataFrame(response.get('companies', []))
