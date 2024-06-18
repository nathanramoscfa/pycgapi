import pandas as pd
from typing import Union

from .base import CoinGeckoAPI


class NFTData(CoinGeckoAPI):
    def nfts_supported(
        self,
        order: str = 'market_cap_usd_desc',
        asset_platform_id: str = None,
        per_page: int = 100,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches a list of all supported NFT ids from CoinGecko, paginated
        by 100 items per page. Allows sorting and filtering based on
        platform and other criteria.

        Args:
            order (str, optional): Order results by fields like
                'market_cap_usd_desc', 'floor_price_native_asc/desc',
                etc. Defaults to 'market_cap_usd_desc'.
            asset_platform_id (str, optional): Platform ID for issuing tokens,
                useful for filtering NFTs from specific platforms.
                See 'asset_platforms' for options. Default is None.
            per_page (int, optional): Results per page, from 1 to 250.
                Default is 100.
            page (int, optional): Page number for pagination. Default is 1.

        Returns:
            pd.DataFrame: Contains list of NFTs with ids, contract addresses,
                names, and other relevant data.

        Notes:
            - Endpoint: 'nfts/list'.
            - Supports pagination and detailed sorting options.
            - Data is refreshed every 5 minutes.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/nfts-list

        """
        endpoint = 'nfts/list'
        params = {
            'order': order,
            'asset_platform_id': asset_platform_id,
            'per_page': per_page,
            'page': page
        }
        response = self._get(endpoint, **params)
        return pd.DataFrame(response).set_index('id')

    def nft_collection_info(
        self,
        nft_id: str = None,
        asset_platform_id: str = None,
        contract_address: str = None
    ) -> pd.DataFrame:
        """
        Fetches current data for a specific NFT collection from the
        CoinGecko API, using either the NFT's ID or its contract address on
        a specified asset platform.

        Args:
            nft_id (str, optional): ID of the NFT collection, obtainable via
                'get_supported_nfts' method.
            asset_platform_id (str, optional): Platform ID issuing tokens,
                useful for querying by contract address. See 'asset_platforms'
                for options.
            contract_address (str, optional): Contract address of the NFT,
                obtainable via 'get_supported_nfts'.

        Returns:
            pd.DataFrame: Contains current data for the specified NFT
                collection including name, floor price, and 24hr volume.

        Notes:
            - Uses endpoints: 'nfts/{id}' and
              'nfts/{asset_platform_id}/contract/{contract_address}'.
            - Data updates every 60 seconds.
            - Not all NFT collections are supported, e.g., Solana NFTs and Art
              Blocks must be queried using 'nfts/{id}'.
            - CoinGecko API Documentation:
              - By ID:
                https://docs.coingecko.com/reference/nfts-id
              - By Contract Address:
                https://docs.coingecko.com/reference/nfts-contract-address

        """
        if nft_id:
            endpoint = f'nfts/{nft_id}'
        elif asset_platform_id and contract_address:
            endpoint = f'nfts/{asset_platform_id}/contract/{contract_address}'
        else:
            raise ValueError(
                "Provide either nft_id or both asset_platform_id and "
                "contract_address")

        response = self._get(endpoint)
        df = pd.DataFrame([response])
        df.set_index('id', inplace=True)
        return df

    def nft_collections_info(
        self,
        nft_ids: list = None,
        asset_platform_id: str = None,
        contract_addresses: list = None
    ) -> pd.DataFrame:
        """
        Fetches current data for multiple NFT collections from CoinGecko,
        using either a list of NFT IDs or a combination of an asset platform
        ID and a list of contract addresses.

        Args:
            nft_ids (list, optional): List of NFT collection IDs, obtainable
                from 'get_supported_nfts'.
            asset_platform_id (str, optional): ID of the platform issuing
                tokens, referenced via 'asset_platforms' endpoint.
            contract_addresses (list, optional): List of contract addresses of
                the NFT collections, used when 'asset_platform_id' is provided.

        Returns:
            pd.DataFrame: Consolidated data of specified NFT collections,
                with each collection's data as a column if multiple collections
                are fetched.

        Notes:
            - See 'nft_collection_info' for more details on the data returned.

        """
        collections_data = {}
        if nft_ids:
            for nft_id in nft_ids:
                df = self.nft_collection_info(nft_id=nft_id)
                collections_data[nft_id] = df
        elif asset_platform_id and contract_addresses:
            for address in contract_addresses:
                df = self.nft_collection_info(
                    asset_platform_id=asset_platform_id,
                    contract_address=address
                )
                collections_data[address] = df

        if collections_data:
            combined_df = pd.concat(collections_data.values(), axis=1)
        else:
            combined_df = pd.DataFrame()

        return combined_df

    def nft_market_data(
        self,
        asset_platform_id: str = None,
        order: str = 'market_cap_usd_desc',
        per_page: int = 100,
        page: int = 1
    ) -> pd.DataFrame:
        """
        Fetches market data for supported NFTs from CoinGecko, including
        market cap and trading volume, with pagination support.

        Args:
            asset_platform_id (str, optional): Platform issuing tokens,
                useful for filtering NFTs from specific blockchain networks.
                Refer to '/asset_platforms filter=nft' for valid platforms.
            order (str, optional): Result sorting criteria, including options
                like 'h24_volume_native_asc', 'market_cap_usd_desc', etc.
                Defaults to 'market_cap_usd_desc'.
            per_page (int, optional): Number of results per page, can be set
                between 1 to 250. Defaults to 100.
            page (int, optional): Page number for results pagination.
                Defaults to 1.

        Returns:
            pd.DataFrame: DataFrame listing NFTs with market data,
                indexed by NFT ID. Includes fields such as floor price,
                market cap, and trading volume.

        Notes:
            - Endpoint: 'nfts/markets'.
            - Data refreshes every 5 minutes.
            - Exclusive for Pro and Enterprise API subscribers.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/nfts-markets

        """
        endpoint = 'nfts/markets'
        params = {
            'asset_platform_id': asset_platform_id,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        response = self._get(endpoint, **params)
        return pd.DataFrame(response).set_index('id')

    def nft_historical_data(
        self,
        nft_id: str = None,
        asset_platform_id: str = None,
        contract_address: str = None,
        days: Union[int, str] = 30
    ) -> pd.DataFrame:
        """
        Retrieves historical market data for a specified NFT collection
        from CoinGecko, including metrics like floor price and market cap.

        Args:
            nft_id (str, optional): ID of the NFT collection. If provided,
                queries historical data using the NFT's ID.
            asset_platform_id (str, optional): Platform issuing tokens. Required
                if querying by contract address.
            contract_address (str, optional): Contract address of the NFT.
                Required if querying with asset platform ID.
            days (Union[int, str]): Time span in days for the data. Can specify
                'max' for maximum available historical data.

        Returns:
            pd.DataFrame: Historical market data indexed by timestamp, including
                various metrics such as floor price in USD, volume, and market
                cap.

        Notes:
            - Endpoints:
              - For NFT ID:
                'nfts/{id}/market_chart'
              - For contract address:
                'nfts/{asset_platform_id}/contract/{contract_address}/market_chart'
            - Data granularity adjusts automatically:
              - 1-14 days = 10-minutely data
              - 15+ days = daily data at 00:00 UTC
            - The last completed UTC day is available 5 minutes after midnight.
            - Exclusively available for Paid Plan Subscribers (Analyst, Lite,
              Pro, and Enterprise).
            - API Documentation:
              - By ID:
                https://pro-api.coingecko.com/api/v3/nfts/{id}/market_chart
              - By Contract Address:
                https://pro-api.coingecko.com/api/v3/nfts/{asset_platform_id}/contract/{contract_address}/market_chart

        """
        if nft_id:
            endpoint = f'nfts/{nft_id}/market_chart'
        elif asset_platform_id and contract_address:
            endpoint = (f'nfts/{asset_platform_id}/contract/'
                        f'{contract_address}/market_chart')
        else:
            raise ValueError(
                "Provide either 'nft_id' or both 'asset_platform_id' "
                "and 'contract_address'")

        params = {'days': days}
        response = self._get(endpoint, **params)
        series_names = ['floor_price_usd', 'floor_price_native',
                        'h24_volume_usd', 'h24_volume_native',
                        'market_cap_usd', 'market_cap_native']

        # Create and merge DataFrames for each series
        dfs = []
        for series_name in series_names:
            series_data = response.get(series_name, [])
            if series_data:
                temp_df = pd.DataFrame(series_data,
                                       columns=['timestamp', series_name])
                temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'],
                                                      unit='ms')
                temp_df.set_index('timestamp', inplace=True)
                dfs.append(temp_df)

        # Merge all series DataFrames
        if dfs:
            merged_df = pd.concat(dfs, axis=1)
        else:
            merged_df = pd.DataFrame()
        return merged_df

    def nft_market_tickers(self, nft_id: str) -> pd.DataFrame:
        """
        Retrieves the latest market ticker data, including floor price
        and 24-hour volume, for an NFT collection across various NFT
        marketplaces.

        Args:
            nft_id (str): ID of the NFT collection to query.

        Returns:
            pd.DataFrame: Contains ticker data such as floor price and
                24h volume for the specified NFT collection.

        Notes:
            - Endpoint: 'nfts/{id}/tickers'.
            - Data updates every 30 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/nfts-id-tickers

        """
        endpoint = f'nfts/{nft_id}/tickers'
        response = self._get(endpoint)
        tickers_data = response.get('tickers', [])
        return pd.DataFrame(tickers_data)
