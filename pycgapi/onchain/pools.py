import pandas as pd

from ..base import CoinGeckoAPI


class Pools(CoinGeckoAPI):
    def trending_pools_list(
        self,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches a list of trending pools across all networks on
        GeckoTerminal. Allows customization of returned attributes.

        Args:
            include (str, optional): Comma-separated attributes to
                include. Possible values: 'base_token', 'quote_token',
                'dex', 'network'. Defaults to 'base_token'.
            page (int, optional): Page number for paginated results,
                maximum 10. Defaults to 1.

        Returns:
            pd.DataFrame: Data on trending pools with specified attributes.

        Notes:
            - Endpoint: onchain/networks/trending_pools
            - Attributes specified in 'include' are shown under "included".
            - Data updates every 60 seconds.
            - Useful for tracking liquidity and popularity trends in
              DeFi ecosystems.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/trending-pools-list

        """
        endpoint = (f"onchain/networks/trending_pools"
                    f"?include={include}&page={page}")
        response = self._get(endpoint)
        data = response['data']

        # Process data and included sections
        included_data = {item['id']: item for item
                         in response.get('included', [])}
        processed_pools = []
        for pool in data:
            pool_details = {**pool['attributes']}
            for rel_key, rel_value in pool['relationships'].items():
                related_id = rel_value['data']['id']
                if related_id in included_data:
                    related_attrs = included_data[related_id]['attributes']
                    pool_details.update({
                        f"{rel_key}_{k}": v for k, v in related_attrs.items()
                    })
            processed_pools.append(pool_details)

        return pd.DataFrame(processed_pools)

    def trending_pools_by_network(
        self,
        network: str = 'eth',
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches trending pools based on the provided network with
        optional attributes included. Useful for tracking liquidity and
        trading activities in DeFi ecosystems.

        Args:
            network (str): Network ID to query dexes (e.g., 'eth').
                Default is 'eth'.
            include (str, optional): Comma-separated attributes to
                include, such as 'base_token', 'quote_token', 'dex'.
                Default is None.
            page (int, optional): Page number for paginated results,
                up to 10. Default is 1.

        Returns:
            pd.DataFrame: Contains data on trending pools on the specified
                network with selected attributes included, indexed by pool ID.

        Notes:
            - Endpoint: onchain/networks/{network}/trending_pools
            - Attributes specified in 'include' are shown under "included".
            - Data refreshes every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/trending-pools-network

        """
        endpoint = f"onchain/networks/{network}/trending_pools"
        params = {'include': include, 'page': page}
        response = self._get(endpoint, **params)
        data = response.get('data', [])
        included_data = {item['id']: item for item
                         in response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {
                **pool.get('attributes', {}),
                'id': pool['id'],
                'type': pool['type']
            }
            for rel_key, rel_value in pool.get('relationships', {}).items():
                related_id = rel_value.get('data', {}).get('id')
                if related_id in included_data:
                    related_attrs = included_data[related_id].get(
                        'attributes', {})
                    pool_details.update({
                        f"{rel_key}_{k}": v for k, v in related_attrs.items()
                    })
            processed_pools.append(pool_details)

        return pd.DataFrame(processed_pools).set_index('id')

    def specific_pool_data_by_address(
        self,
        network: str,
        address: str,
        include: str = None
    ) -> pd.DataFrame:
        """
        Retrieves detailed data for a specific pool based on the network
        and pool address. Optionally includes specified attributes such
        as base token, quote token, and dex information.

        Args:
            network (str): The network ID (e.g., 'eth').
            address (str): The pool's contract address.
            include (str, optional): Comma-separated attributes to
                include in the response. Available values are 'base_token',
                'quote_token', 'dex'. Defaults to None.

        Returns:
            pd.DataFrame: Data for the specified pool, structured in rows
                with the pool's attributes and any included data.

        Notes:
            - Endpoint: 'onchain/networks/{network}/pools/{address}'
            - Includes additional attributes under the "included" key if
              specified.
            - Data updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/pool-address

        """
        params = {'include': include} if include else {}
        response = self._get(
            f"onchain/networks/{network}/pools/{address}", **params)
        data = response.get('data', {})
        attributes = data.get('attributes', {})
        relationships = data.get('relationships', {})

        # Prepare the main pool data
        processed_pool_data = {
            **attributes, 'id': data.get('id'), 'type': data.get('type')}

        # Process included data if any
        included_data = {item['id']: item for item
                         in response.get('included', [])}
        for rel_key in include.split(','):
            if rel_key in relationships:
                rel_data = relationships[rel_key].get('data', {})
                related_item_id = rel_data.get('id')
                if related_item_id in included_data:
                    related_item_attrs = included_data[related_item_id].get(
                        'attributes', {})
                    processed_pool_data.update({
                        f"{rel_key}_{attr}": val for attr,
                        val in related_item_attrs.items()
                    })

        return pd.DataFrame([processed_pool_data]).set_index('id').T

    def multiple_pools_data_by_addresses(
        self,
        network: str,
        addresses: list,
        include: str = None
    ) -> pd.DataFrame:
        """
        Fetches data for multiple pools based on the provided network
        and pool addresses.

        Args:
            network (str): The network ID (e.g., 'eth').
            addresses (list): A list of pool addresses.
            include (str, optional): Comma-separated attributes to
                include. Available values: 'base_token', 'quote_token',
                'dex'. Default is an empty string.

        Returns:
            pd.DataFrame: Data for the specified pools.

        Notes:
            - Endpoint: onchain/networks/{network}/pools/multi/{addresses_str}
            - Includes additional attributes under the "included" key.
            - Cache/Update frequency: every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/pools-addresses
        """
        addresses_str = ','.join(addresses)
        params = {'include': include} if include else {}
        response = self._get(
            f"onchain/networks/{network}/pools/multi/{addresses_str}",
            **params
        )
        data = response.get('data', [])

        # Initialize included_data to ensure it's always defined
        included_data = {item['id']: item for item in
                         response.get('included', [])}

        # Process each pool's data
        processed_pools_data = []
        for pool in data:
            pool_data = {**pool.get('attributes', {}), 'id': pool['id']}
            for rel_key in include.split(','):
                rel_data = pool.get('relationships', {}).get(rel_key, {}).get(
                    'data', {})
                if rel_data:
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_data.update(
                            {f"{rel_key}_{attr}": val for attr, val in
                             related_attrs.items()})

            processed_pools_data.append(pool_data)

        return pd.DataFrame(processed_pools_data).set_index('id')

    def top_pools_by_network(
        self,
        network: str,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches data for all the top pools based on the provided network,
        optionally including specified attributes such as 'base_token',
        'quote_token', and 'dex'.

        Args:
            network (str): The network ID (e.g., 'eth').
            include (str, optional): Attributes to include, comma-separated if
                more than one. Available values are 'base_token', 'quote_token',
                'dex'. Defaults to None.
            page (int, optional): Page number to paginate through results,
                up to a maximum of 10 pages. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the top pools on
                the specified network, potentially enriched with included data.

        Notes:
            - Endpoint: 'onchain/networks/{network}/pools'
            - Includes additional attributes under the "included" key.
            - Cache/Update frequency: every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/top-pools-network

        """
        params = {'page': page}
        if include:
            params['include'] = include
        response = self._get(
            f"onchain/networks/{network}/pools", **params)
        data = response.get('data', [])
        df = pd.json_normalize(data)  # Normalize the main pool data

        # Simplify column names by removing common prefixes and redundant info
        df.columns = [
            col.replace('attributes.', '').replace('relationships.', 'rel_')
            for col in df.columns]

        if 'included' in response:
            included = response['included']
            included_df = pd.json_normalize(included).set_index('id')
            included_df.columns = ['inc_' + col for col in
                                   included_df.columns]  # Prefix for clarity
            for rel_key in include.split(','):
                rel_col = f'rel_{rel_key}_data.id'
                if rel_col in df.columns:
                    df = df.join(included_df, on=rel_col, rsuffix=f'_{rel_key}')

        return df.set_index('id')

    def top_pools_by_dex(
        self,
        network: str,
        dex: str,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches data for all the top pools based on the provided network
        and decentralized exchange (DEX).

        Args:
            network (str): The network ID (e.g., 'eth').
            dex (str): The dex ID (e.g., 'sushiswap').
            include (str, optional): Attributes to include, comma-separated.
                Available values: 'base_token', 'quote_token', 'dex'.
                Defaults to None.
            page (int, optional): Page number to paginate through results,
                up to a maximum of 10 pages. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the top
                pools on the specified network's dex, potentially enriched
                with additional included attributes.

        Notes:
            - Endpoint: 'onchain/networks/{network}/dexes/{dex}/pools'
            - Attributes specified in the include params will be included
              under the "included" key.
            - Data updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/top-pools-dex

        """
        params = {'page': page, 'include': include} if include else {
            'page': page}
        response = self._get(
            f"onchain/networks/{network}/dexes/{dex}/pools",
            **params
        )
        data = response.get('data', [])
        included_data = {item['id']: item for item in
                         response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {**pool.get('attributes', {}), 'id': pool['id']}
            # Process relationships if any
            for rel_key in include.split(','):
                if rel_key in pool.get('relationships', {}):
                    rel_data = pool['relationships'][rel_key].get('data', {})
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_item_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_details.update({
                            f"{rel_key}_{attr}": val for attr, val in
                            related_item_attrs.items()
                        })
            processed_pools.append(pool_details)

        return pd.DataFrame(processed_pools).set_index('id')

    def new_pools_by_network(
        self,
        network: str,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches data for all the latest pools based on the provided network,
        optionally including additional attributes.

        Args:
            network (str): Network ID where the pools are located (e.g., 'eth').
            include (str, optional): Comma-separated attributes to include.
                Available options are 'base_token', 'quote_token', 'dex'.
                Defaults to None.
            page (int, optional): Page number for paginated results, up to a
                maximum of 10 pages. Defaults to 1.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the latest pools
                on the specified network, potentially enriched with additional
                included attributes.

        Notes:
            - Endpoint: 'onchain/networks/{network}/new_pools'
            - Attributes specified in 'include' will appear under the "included"
              key.
            - Data is refreshed every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/latest-pools-network

        """
        params = {'page': page, 'include': include} \
            if include else {'page': page}
        response = self._get(
            f"onchain/networks/{network}/new_pools", **params)
        data = response.get('data', [])
        included_data = {item['id']: item for item in
                         response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {**pool.get('attributes', {}), 'id': pool['id']}
            for rel_key in include.split(','):
                if rel_key in pool.get('relationships', {}):
                    rel_data = pool['relationships'][rel_key].get('data', {})
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_item_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_details.update({
                            f"{rel_key}_{attr}": val for attr, val in
                            related_item_attrs.items()
                        })
            processed_pools.append(pool_details)

        return pd.DataFrame(processed_pools).set_index('id')

    def new_pools_list(
        self,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches data for all the latest pools across all networks on
        GeckoTerminal, allowing for detailed inclusion of specific attributes.

        Args:
            include (str, optional): Attributes to include, comma-separated.
                Possible values: 'base_token', 'quote_token', 'dex', 'network'.
            page (int, optional): Page number for results, maximum of 10 pages.
                Defaults to 1.

        Returns:
            pd.DataFrame: Data for the latest pools across all networks,
                including any specified attributes.

        Notes:
            - Endpoint: 'onchain/networks/new_pools'
            - Attributes specified in 'include' are detailed under the
              "included" key.
            - Data is updated every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/latest-pools-list
        """
        params = {'page': page, 'include': include} if include else {
            'page': page}
        response = self._get(f"onchain/networks/new_pools", **params)
        data = response.get('data', [])
        included_data = {item['id']: item for item in
                         response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {**pool.get('attributes', {}), 'id': pool['id']}
            for rel_key in include.split(','):
                if rel_key in pool.get('relationships', {}):
                    rel_data = pool['relationships'][rel_key].get('data', {})
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_item_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_details.update({
                            f"{rel_key}_{attr}": val for attr, val in
                            related_item_attrs.items()
                        })
            processed_pools.append(pool_details)

        df = pd.DataFrame(processed_pools)
        return df.set_index('id')

    def search_pools(
        self,
        query: str,
        network: str,
        include: str = None,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Searches for pools based on a query within a specific network,
        optionally including additional attributes.

        Args:
            query (str): Search query, e.g., pool address, token address.
            network (str): Network ID, such as 'eth' for Ethereum.
            include (str, optional): Attributes to include, comma-separated.
                Options: 'base_token', 'quote_token', 'dex'. Defaults to None.
            page (int, optional): Page number for results, up to 10.
                Defaults to 1.

        Returns:
            pd.DataFrame: DataFrame with matched pools data and additional
                included attributes.

        Notes:
            - Endpoint: 'onchain/search/pools'
            - Updates every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/search-pools

        """
        params = {'query': query, 'network': network, 'page': page,
                  'include': include}
        response = self._get(f"onchain/search/pools", **params)
        data = response.get('data', [])
        included_data = {item['id']: item for item in
                         response.get('included', [])}

        processed_pools = []
        for pool in data:
            pool_details = {**pool.get('attributes', {}), 'id': pool['id']}
            for rel_key in include.split(','):
                if rel_key in pool.get('relationships', {}):
                    rel_data = pool['relationships'][rel_key].get('data', {})
                    related_item_id = rel_data.get('id')
                    if related_item_id in included_data:
                        related_item_attrs = included_data[related_item_id].get(
                            'attributes', {})
                        pool_details.update({
                            f"{rel_key}_{attr}": val for attr, val in
                            related_item_attrs.items()
                        })
            processed_pools.append(pool_details)

        df = pd.DataFrame(processed_pools)
        return df.set_index('id')
