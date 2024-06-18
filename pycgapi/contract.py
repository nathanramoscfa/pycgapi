import pandas as pd
import pytz
from typing import Union

from .base import CoinGeckoAPI
from .utils import convert_to_unix


class Contract(CoinGeckoAPI):
    def coin_by_contract(self, platform_id: str, contract_address: str) -> dict:
        """
        Fetches detailed token information from CoinGecko based on its contract
        address.

        Args:
            platform_id (str): Blockchain platform ID (e.g., 'ethereum').
            contract_address (str): Contract address of the token.

        Returns:
            dict: Token data including name, price, market data, and exchange
                tickers.

        Notes:
            - Endpoint: coins/{platform_id}/contract/{contract_address}
            - Data updated every 60 seconds.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-contract-address

        """
        endpoint = f'coins/{platform_id}/contract/{contract_address}'
        return self._get(endpoint)

    def contract_historical_market_data(
        self,
        platform_id: str,
        contract_address: str,
        vs_currency: str = 'usd',
        days: Union[int, str] = 30,
        from_date: str = None,
        to_date: str = None,
        precision: str = None,
        timezone_str: str = 'UTC'
    ) -> pd.DataFrame:
        """
        Retrieves historical market data for a token from its contract address,
        detailing price metrics over specific timeframes.

        Args:
            platform_id (str): ID where the token is hosted (e.g., 'ethereum').
            contract_address (str): Token's contract address.
            vs_currency (str, optional): Market data currency. Default is 'usd'.
            days (Union[int, str], optional): Days ago or 'max'. Default is 30.
            from_date (str, optional): Start date in 'mm-dd-yyyy' or UNIX stamp.
            to_date (str, optional): End date in 'mm-dd-yyyy' or UNIX stamp.
            precision (str, optional): Decimal precision of price.
            timezone_str (str, optional): Timezone for dates. Default is 'UTC'.

        Returns:
            pd.DataFrame: Contains timestamps, prices, market cap, and volume
                data formatted to the specified timezone.

        Notes:
            - Data granularity depends on the selected time range.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/coins-id-contract-market-chart

        """
        from_timestamp = convert_to_unix(from_date) if from_date else None
        to_timestamp = convert_to_unix(to_date) if to_date else None

        if from_timestamp and to_timestamp:
            endpoint = (f'coins/{platform_id}/contract/{contract_address}/'
                        f'market_chart/range')
            params = {
                'vs_currency': vs_currency,
                'from': from_timestamp,
                'to': to_timestamp,
                'precision': precision
            }
        else:
            endpoint = (f'coins/{platform_id}/contract/{contract_address}/'
                        f'market_chart')
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'precision': precision
            }

        response = self._get(endpoint, **params)
        df = pd.DataFrame({
            'timestamp': [ts[0] for ts in response['prices']],
            'price': [price[1] for price in response['prices']],
            'market_cap': [mc[1] for mc in response['market_caps']],
            'total_volume': [vol[1] for vol in response['total_volumes']]
        })

        tz = pytz.timezone(timezone_str)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['timestamp'] = df['timestamp'].dt.tz_convert(tz)
        df['timestamp'] = df['timestamp'].apply(
            lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0))
        df.set_index('timestamp', inplace=True)
        return df
