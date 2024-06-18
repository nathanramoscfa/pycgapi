import pandas as pd

from ..base import CoinGeckoAPI


class Tokens(CoinGeckoAPI):
    def top_pools_by_token_address(
        self,
        network: str,
        token_address: str,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches top pools for a token on a network.

        Args:
            network (str): Network ID (e.g., 'eth').
            token_address (str): Token contract address.
            include (str, optional): Comma-separated attributes to
                include. Possible values: 'base_token', 'quote_token',
                'dex'. Defaults to None.
            page (int, optional): Page number, up to 10. Defaults to 1.

        Returns:
            pd.DataFrame: Data of top pools for the token.

        Notes:
            - Endpoint: onchain/networks/{network}/tokens/{token_address}/pools
            - Attributes in 'include' shown under "included" key.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/top-pools-contract-address

        """
        params = {'page': page}
        if include:
            params['include'] = include
        endpoint = f"onchain/networks/{network}/tokens/{token_address}/pools"
        response = self._get(endpoint, **params)
        data = response.get('data', [])
        included_data = {item['id']: item for item
                         in response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {**pool.get('attributes', {}), 'id': pool['id']}
            relationships = pool.get('relationships', {})
            for rel_key in include.split(',') if include else []:
                if rel_key in relationships:
                    rel_data = relationships[rel_key].get('data', {})
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_details.update({
                            f"{rel_key}_{k}": v for k, v
                            in related_attrs.items()
                        })
            processed_pools.append(pool_details)

        return pd.DataFrame(processed_pools).set_index('id')

    def token_data_by_address(
        self,
        network: str,
        address: str,
        include: str = None
    ) -> pd.DataFrame:
        """
        Fetches specific token data based on the token contract address
        on a specified network.

        Args:
            network (str): The network ID (e.g., 'eth').
            address (str): The token contract address.
            include (str, optional): Attributes to include, such as
                'top_pools' to include top pools information. Default
                is None.

        Returns:
            pd.DataFrame: DataFrame with specific token data.

        Notes:
            - Endpoint: onchain/networks/{network}/tokens/{address}
            - Attributes in 'include' are shown under "included" key.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/token-data-contract-address

        """
        params = {'include': include} if include else {}
        response = self._get(
            f"onchain/networks/{network}/tokens/{address}", **params)
        data = response.get('data', {})

        if data:
            # Flatten attributes and relationships into DataFrames
            attributes_df = pd.json_normalize(data.get('attributes', {}))
            relationships_df = pd.json_normalize(
                data.get('relationships', {}), sep='_')

            # Merge DataFrames and rename columns to remove nested labels
            df = pd.concat([attributes_df, relationships_df], axis=1).T
            df.index = [
                idx.replace('attributes.', '').replace('relationships.', '')
                for idx in df.index]
        else:
            df = pd.DataFrame()

        return df

    def tokens_data_by_addresses(
        self,
        network: str,
        addresses: list,
        include: str = None
    ) -> pd.DataFrame:
        """
        Fetches data for multiple tokens on a specified network.

        Args:
            network (str): Network ID (e.g., 'eth').
            addresses (list): Token contract addresses.
            include (str, optional): Comma-separated attributes to
                include, such as 'top_pools'. Defaults to None.

        Returns:
            pd.DataFrame: Data for multiple tokens.

        Notes:
            - Endpoint: onchain/networks/{network}/tokens/multi/
            - Only returns the first top pool if 'top_pools' is included.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/tokens-data-contract-addresses
        """
        addresses_str = ','.join(addresses)
        params = {'include': include} if include else {}
        response = self._get(
            f"onchain/networks/{network}/tokens/multi/{addresses_str}",
            **params)
        data = response.get('data', [])

        # Process each token's data
        token_data = []
        for token in data:
            details = token.get('attributes', {})
            token_id = token.get('id')
            processed_details = {key: value for key, value in details.items()}
            processed_details['id'] = token_id

            if include:
                # Process included data based on relationships
                included_data = {item['id']: item for item
                                 in response.get('included', [])}
                relationships = token.get('relationships', {})
                for rel_key in include.split(',') if include else []:
                    rel_items = relationships.get(rel_key, {}).get('data', [])
                    for rel_item in rel_items:
                        related_item_id = rel_item.get('id')
                        if related_item_id in included_data:
                            related_attrs = included_data[related_item_id].get(
                                'attributes', {})
                            for attr, val in related_attrs.items():
                                processed_details[f"{rel_key}_{attr}"] = val
            token_data.append(processed_details)

        df = pd.DataFrame(token_data)
        if token_data:
            df.index = [item['id'] for item in data]
        return df

    def token_info_by_address(
        self,
        network: str,
        address: str
    ) -> pd.DataFrame:
        """
        Fetches specific token information based on a token contract
        address on a specified network.

        Args:
            network (str): Network ID (e.g., 'eth').
            address (str): Token contract address.

        Returns:
            pd.DataFrame: Token information including name, symbol,
                and CoinGecko ID.

        Notes:
            - Endpoint: onchain/networks/{network}/tokens/{address}/info
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/token-info-contract-address
        """
        endpoint = f"onchain/networks/{network}/tokens/{address}/info"
        response = self._get(endpoint)
        data = response.get('data', {})

        if data:
            # Flatten attributes and relationships into DataFrames
            attributes_df = pd.json_normalize(data.get('attributes', {}))
            relationships_df = pd.json_normalize(
                data.get('relationships', {}), sep='_')

            # Merge DataFrames and rename columns to remove nested labels
            df = pd.concat([attributes_df, relationships_df], axis=1).T
            df.index = [
                idx.replace('attributes.', '').replace('relationships.', '')
                for idx in df.index]
        else:
            df = pd.DataFrame()

        return df

    def pool_tokens_info_by_pool_address(
        self,
        network: str,
        pool_address: str
    ) -> pd.DataFrame:
        """
        Queries pool info, including token data, based on pool address.

        Args:
            network (str): Network ID (e.g., 'eth').
            pool_address (str): Pool contract address.

        Returns:
            pd.DataFrame: Info of the pool including tokens.

        Notes:
            - Endpoint: onchain/networks/{network}/pools/{pool_address}/info
            - For additional pool data like transactions, use
              /networks/{network}/pools/{address}.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/pool-token-info-contract-address
        """
        endpoint = f"onchain/networks/{network}/pools/{pool_address}/info"
        response = self._get(endpoint)
        data = response.get('data', {})

        if data:
            # Normalize data and set index to 'id' if present
            df = pd.json_normalize(data).set_index('id')
        else:
            df = pd.DataFrame()

        return df

    def most_recently_updated_tokens_list(
        self,
        include: str = None
    ) -> pd.DataFrame:
        """
        Queries info for the 100 most recently updated tokens across
        all networks on GeckoTerminal.

        Args:
            include (str, optional): Attributes to include,
                comma-separated if more than one. Possible values such as
                'network' to include network details with the token list.

        Returns:
            pd.DataFrame: Data of the 100 most recently updated tokens,
                ordered by most recent updates.

        Notes:
            - Attributes in 'include' are shown under "included" key.
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/tokens-info-recent-updated
        """
        endpoint = "onchain/tokens/info_recently_updated"
        params = {'include': include} if include else {}
        response = self._get(endpoint, **params)
        data = response.get('data', [])

        # Normalize and return the DataFrame
        df = pd.json_normalize(data) if data else pd.DataFrame()
        return df.set_index('id')
