import pandas as pd

from ..base import CoinGeckoAPI


class OHLCV(CoinGeckoAPI):
    def pool_ohlcv_by_address(
        self,
        network: str,
        pool_address: str,
        timeframe: str = 'day',
        aggregate: int = 1,  # Changed to int
        before_timestamp: int = None,
        limit: int = 100,
        currency: str = 'usd',
        token: str = None
    ) -> pd.DataFrame:
        """
        Fetches OHLCV (Open, High, Low, Close, Volume) data for a pool based
        on the pool address within a specified network.

        Args:
            network (str): Network ID where the pool is located (e.g., 'eth').
            pool_address (str): Contract address of the pool.
            timeframe (str, optional): Timeframe for the OHLCV data, such as
                'minute', 'hour', or 'day'. Default is 'day'.
            aggregate (int, optional): The time period, in units of the
                timeframe, to aggregate data. Defaults to 1.
            before_timestamp (int, optional): Filter data to before this
                epoch/unix timestamp. Default is None.
            limit (int, optional): Maximum number of data points to return.
                Maximum is 1000. Default is 100.
            currency (str, optional): Currency in which to display price data.
                Defaults to 'usd'.
            token (str, optional): Specify 'base', 'quote', or a token address
                to tailor the returned data. Default is None.

        Returns:
            pd.DataFrame: A DataFrame with columns for the timestamp, open,
                high, low, close, and volume of the pool.

        Notes:
            - Endpoint:
              'onchain/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}'
            - Data updates every 60 seconds.
            - Only pools with up to two tokens are supported.
            - Data is available up to 6 months prior. If no data is available,
              an empty DataFrame is returned.
            - CoinGecko API doc:
              https://docs.coingecko.com/reference/pool-ohlcv-contract-address
        """
        params = (f"?aggregate={str(aggregate)}"
                  f"&limit={limit}&currency={currency}")
        if before_timestamp:
            params += f"&before_timestamp={before_timestamp}"
        if token:
            params += f"&token={token}"
        endpoint = (f"onchain/networks/{network}/pools/{pool_address}/ohlcv/"
                    f"{timeframe}{params}")
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()
        data = response.json()

        # Extract and convert OHLCV data to DataFrame
        ohlcv_list = data['data']['attributes']['ohlcv_list']
        df = pd.DataFrame(ohlcv_list,
                          columns=['timestamp', 'open', 'high', 'low', 'close',
                                   'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.strftime(
            '%m-%d-%Y')
        df.set_index('timestamp', inplace=True)

        return df
