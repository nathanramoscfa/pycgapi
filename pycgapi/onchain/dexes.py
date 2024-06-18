import pandas as pd

from ..base import CoinGeckoAPI


class Dexes(CoinGeckoAPI):
    def supported_dexes_list(self, network: str, page: int = 1) -> pd.DataFrame:
        """
        Fetches a list of supported decentralized exchanges (DEXs)
        for a specified network on CoinGecko.

        Args:
            network (str): Network ID to query DEXs (e.g., 'ethereum').
            page (int, optional): Page number for results pagination.
                Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the list of DEXs with
                their IDs and names for the specified network.

        Notes:
            - Endpoint: 'onchain/networks/{network}/dexes'.
            - Ensure the network matches IDs from the /networks endpoint.
            - Data is updated every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/dexes

        """
        endpoint = f"onchain/networks/{network}/dexes?page={page}"
        response = self._get(endpoint)
        data = response['data']
        return pd.DataFrame(data)
