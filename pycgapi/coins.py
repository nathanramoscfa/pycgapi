from .base import CoinGeckoAPI
from .historical_data import HistoricalData
from .market_data import MarketData
from .ohlc_data import OHLCData
from .ticker_data import TickerData


class Coins:
    """
    Initializes an interface to access various cryptocurrency data from
    CoinGecko, including market, historical, ticker, and OHLC data. This
    class manages efficient connection via a shared HTTP session across
    all submodules, optimizing network resource use.

    Attributes:
        api (CoinGeckoAPI): Handles general API requests.
        historical_data (HistoricalData): Manages historical data retrieval.
        market_data (MarketData): Retrieves live market data.
        ohlc_data (OHLCData): Retrieves open, high, low, and close data.
        ticker_data (TickerData): Provides access to ticker information.

    Parameters:
        api_key (str, optional): API key for authenticated CoinGecko requests.
        pro_api (bool, optional): Use the PRO API for enhanced data access.

    """

    def __init__(self, api_key=None, pro_api=False):
        self.api = CoinGeckoAPI(api_key, pro_api)
        self.historical_data = HistoricalData(api_key, pro_api)
        self.market_data = MarketData(api_key, pro_api)
        self.ohlc_data = OHLCData(api_key, pro_api)
        self.ticker_data = TickerData(api_key, pro_api)

    @classmethod
    def end_session(cls):
        """
        Closes the shared HTTP session among all instances and ensures
        clean shutdown of resources, resetting the session attribute
        to None.

        """
        CoinGeckoAPI.end_session()
