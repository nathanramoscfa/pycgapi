import pandas as pd

from .base import CoinGeckoAPI


class AssetPlatforms(CoinGeckoAPI):
    def asset_platforms_list(self, platform_filter: str = None) -> pd.DataFrame:
        """
        Queries CoinGecko for asset platforms, optionally filtering for
        platforms that support NFTs.

        Args:
            platform_filter (str, optional): 'nft' to filter for NFT-supporting
                platforms; defaults to None for all platforms.

        Returns:
            pd.DataFrame: Details such as platform identifiers.

        Notes:
            - Endpoint: 'asset_platforms'.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/asset-platforms-list

        """
        endpoint = "asset_platforms"
        params = {'filter': platform_filter} if platform_filter else {}
        response = self._get(endpoint, **params)
        return pd.DataFrame(response)

    def all_tokens_list(self, asset_platform_id: str) -> pd.DataFrame:
        """
        Retrieves a list of tokens for a specified blockchain network, adhering
        to the Ethereum token list standard.

        Args:
            asset_platform_id (str): Blockchain network ID (e.g., 'ethereum').

        Returns:
            pd.DataFrame: Tokens for the network, adhering to list standards.

        Notes:
            - Endpoint: token_lists/{asset_platform_id}/all
            - Data updates every 5 minutes.
            - Exclusive to Enterprise Plan subscribers.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/token-lists

        """
        endpoint = f'token_lists/{asset_platform_id}/all.json'
        response = self._get(endpoint)
        tokens = response.get('tokens', [])
        return pd.DataFrame(tokens)
