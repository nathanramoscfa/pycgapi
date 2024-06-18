import pandas as pd

from ..base import CoinGeckoAPI


class Networks(CoinGeckoAPI):
    def supported_networks_list(self, page: int = 1) -> pd.DataFrame:
        """
        Fetches a list of supported blockchain networks from GeckoTerminal,
        useful for identifying network IDs needed for other API queries.

        Args:
            page (int, optional): Page number for pagination of results.
                Defaults to 1.

        Returns:
            pd.DataFrame: Contains detailed information about each supported
                network, including network IDs and names.

        Notes:
            - Endpoint: 'onchain/networks'.
            - This endpoint helps in retrieving network IDs necessary for
              specifying network-specific data in other API requests.
            - Pagination is supported, allowing navigation through multiple
              pages of network listings.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/networks-list

        """
        endpoint = f"onchain/networks?page={page}"
        response = self._get(endpoint)
        data = response['data']  # Direct access to 'data'

        # Flatten data for DataFrame
        flat_data = [{
            'id': item['id'],
            **item['attributes']  # Merge attributes
        } for item in data]

        return pd.DataFrame(flat_data)
