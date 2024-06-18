import pandas as pd

from ..base import CoinGeckoAPI


class Trades(CoinGeckoAPI):
    def past_24h_trades_by_pool_address(
        self,
        network: str,
        pool_address: str,
        trade_volume_in_usd_greater_than: float = 0
    ) -> pd.DataFrame:
        """
        Fetches the last 300 trades from the past 24 hours for a
        specified pool.

        Args:
            network (str): Network ID (e.g., 'eth').
            pool_address (str): Pool contract address.
            trade_volume_in_usd_greater_than (float, optional): Filter
                trades with volume greater than this value in USD.
                Default is 0.

        Returns:
            pd.DataFrame: DataFrame containing the last 300 trades.

        Notes:
            - Cache/Update frequency: every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/pool-trades-contract-address
        """
        params = (f"?trade_volume_in_usd_greater_than="
                  f"{trade_volume_in_usd_greater_than}")
        endpoint = (f"onchain/networks/{network}/pools/{pool_address}/trades"
                    f"{params}")
        complete_endpoint = self.build_endpoint(endpoint)
        response = self.session.get(complete_endpoint)
        response.raise_for_status()
        data = response.json()

        if 'data' in data:
            df = pd.json_normalize(data['data'])
            df.columns = df.columns.str.replace('attributes.', '')
        else:
            df = pd.DataFrame()

        return df.set_index('id')
