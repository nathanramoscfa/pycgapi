import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

import pandas as pd
from pytz import utc

import mock_responses as mock
from pycgapi import CoinGeckoAPI


class TestCoinGeckoAPI(unittest.TestCase):

    # ------ Set up the API for testing ------ #
    def setUp(self):
        self.initialize_api()

    # Helper method to initialize the API with custom settings
    def initialize_api(self, api_key='test_api_key', pro_api=False, retries=5):
        """Helper method to initialize the API with custom settings."""
        self.api = CoinGeckoAPI(api_key=api_key, pro_api=pro_api, retries=retries)

    # ------ Testing class initialization ------ #
    def test_initialization_with_default_values(self):
        """Test CoinGeckoAPI initialization with default values."""
        self.assertEqual(self.api.api_key, 'test_api_key')
        self.assertFalse(self.api.pro_api)
        self.assertEqual(self.api.base_url, CoinGeckoAPI.API_BASE_URL)

    def test_initialization_with_pro_api(self):
        """Test CoinGeckoAPI initialization with the PRO API flag enabled."""
        self.initialize_api(pro_api=True)
        self.assertTrue(self.api.pro_api)
        self.assertEqual(self.api.base_url, CoinGeckoAPI.PRO_API_BASE_URL)

    def test_retry_settings(self):
        """Test if the retry settings are correctly initialized."""
        self.initialize_api(retries=5)
        adapter = self.api.session.get_adapter('https://')
        self.assertEqual(adapter.max_retries.total, 5)

    def test_construct_endpoint_for_pro_api(self):
        """Test endpoint construction for the PRO API."""
        self.initialize_api(pro_api=True)
        endpoint = self.api.build_endpoint('test_endpoint')
        expected = f'{CoinGeckoAPI.PRO_API_BASE_URL}test_endpoint?x_cg_pro_api_key=test_api_key'
        self.assertEqual(endpoint, expected)

    def test_construct_endpoint_for_standard_api(self):
        """Test endpoint construction for the standard API."""
        self.initialize_api(pro_api=False)
        endpoint = self.api.build_endpoint('test_endpoint')
        expected = f'{CoinGeckoAPI.API_BASE_URL}test_endpoint'
        self.assertEqual(endpoint, expected)

    def test_close_session_success(self):
        """Test successful session closure."""
        response = self.api.end_session()
        self.assertEqual(response, "Session closed successfully.")

    @patch('requests.Session.close')
    def test_close_session_failure(self, mock_close):
        """Test session closure handling failure."""
        mock_close.side_effect = Exception('Test Error')
        response = self.api.end_session()
        self.assertEqual(response, "Error closing session: Test Error")

    @patch('requests.Session.get')
    def test_status_check(self, mock_get):
        """Test the ping method to check API server status."""
        mock_get.return_value.json.return_value = mock.ping_response
        response = self.api.status_check()
        self.assertEqual(response, mock.ping_response)

    # ---------- SIMPLE ---------- #

    # ---------- /simple/price ---------- #
    @patch('requests.Session.get')
    def test_get_simple_prices_by_id(self, mock_get):
        """Test fetching simple prices for cryptocurrencies."""
        # Prepare mock responses
        mock_get.side_effect = [MagicMock(json=lambda: mock.simple_price_response)]

        # Test cryptocurrency prices
        df_crypto = self.api.simple_prices(coin_ids=['bitcoin'], vs_currencies=['usd'])
        expected_df_crypto = pd.DataFrame.from_dict(mock.simple_price_response, orient='index')
        pd.testing.assert_frame_equal(df_crypto, expected_df_crypto)

    # ---------- /simple/price?precision=2 ---------- #
    @patch('requests.Session.get')
    def test_get_simple_prices_by_id_with_precision(self, mock_get):
        """Test fetching simple prices for cryptocurrencies."""
        # Prepare mock responses
        mock_get.side_effect = [MagicMock(json=lambda: mock.simple_price_response)]

        # Test cryptocurrency prices with precision
        precision = '2'
        df_crypto = self.api.simple_prices(coin_ids=['bitcoin'], vs_currencies=['usd'], precision=precision)

        # Modify the expected response based on the precision
        expected_response_modified = {
            'bitcoin': {
                'usd': round(mock.simple_price_response['bitcoin']['usd'], int(precision))
            }
        }
        expected_df_crypto = pd.DataFrame.from_dict(expected_response_modified, orient='index')

        pd.testing.assert_frame_equal(df_crypto, expected_df_crypto)

    # ---------- /simple/token_price/{platform_id} ---------- #
    @patch('requests.Session.get')
    def test_get_simple_prices_by_contract(self, mock_get):
        """Test fetching simple prices for cryptocurrencies."""
        # Prepare mock responses
        mock_get.side_effect = [MagicMock(json=lambda: mock.simple_token_price_response)]

        # Test token prices
        df_token = self.api.simple_prices(coin_ids=['0x5a98fcbea516cf06857215779fd812ca3bef1b32'],
                                          vs_currencies=['usd'],
                                          platform_id='ethereum',
                                          contract_addresses=['0x5a98fcbea516cf06857215779fd812ca3bef1b32'])

        expected_df_token = pd.DataFrame.from_dict(mock.simple_token_price_response, orient='index')
        pd.testing.assert_frame_equal(df_token, expected_df_token)

    # ---------- /simple/supported_vs_currencies ---------- #
    @patch('requests.Session.get')
    def test_get_supported_vs_currencies(self, mock_get):
        """Test fetching supported versus currencies."""
        # Mock the API response
        mock_get.return_value = MagicMock(json=lambda: mock.simple_supported_vs_currencies_response)

        # Call the method
        supported_currencies = self.api.supported_currencies()

        # Assert that the returned list matches the mock response
        self.assertEqual(supported_currencies, mock.simple_supported_vs_currencies_response)

    # ---------- COINS ---------- #

    # ---------- /coins/list ---------- #
    @patch('requests.Session.get')
    def test_get_coins_list_default(self, mock_get):
        """Test the get_coins_list method with default parameters."""
        # Use the mock data from coins_list_mock.py
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_list_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.coins_list()

        # Convert mock response to DataFrame for comparison
        expected_df = pd.DataFrame(mock.coins_list_response).set_index('id')

        # Check if the response is as expected
        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/list?include_platform=true ---------- #
    @patch('requests.Session.get')
    def test_get_coins_list_with_platform(self, mock_get):
        """Test the get_coins_list method with include_platform set to True."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_list_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.coins_list(include_platform=True)

        # Check if the response is as expected
        expected_df = pd.DataFrame(mock.coins_list_response).set_index('id')

        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/markets ---------- #
    @patch('requests.Session.get')
    def test_coins_market_data_default(self, mock_get):
        """Test the get_coins_markets method with default parameters."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_markets_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.coins_market_data()

        # Check if the response is as expected
        expected_df = pd.DataFrame(mock.coins_markets_response).set_index('id')

        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/markets?vs_currency=eur&ids=litecoin ---------- #
    @patch('requests.Session.get')
    def test_coins_market_data_custom_params(self, mock_get):
        """Test the get_coins_markets method with custom parameters."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_markets_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.coins_market_data(vs_currency='eur', ids='litecoin')

        # Check if the response is as expected
        expected_df = pd.DataFrame(mock.coins_markets_response).set_index('id')

        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/markets for multiple coin ids ---------- #
    @patch('pycgapi.CoinGeckoAPI.coins_market_data')
    def test_top_coins_market_data(self, mock_get):
        """Test fetching market data for top N cryptocurrencies."""
        # Mock response for coins_market_data
        mock_get.side_effect = [
            pd.DataFrame({'id': [f'coin{i}' for i in range(1, 251)], 'market_cap': [i for i in range(250, 0, -1)]}),
            pd.DataFrame({'id': [f'coin{i}' for i in range(251, 501)], 'market_cap': [i for i in range(500, 250, -1)]})
        ]

        # Call the method
        top_n = 250
        df = self.api.top_coins_market_data(top_n=top_n)

        # Check if the response contains the correct number of rows
        self.assertEqual(len(df), top_n)

    # ---------- /coins/{id} ---------- #
    @patch('requests.Session.get')
    def test_coin_info(self, mock_get):
        """Test fetching data for a specific coin."""
        # Mock response for get_coin_data
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_response
        mock_get.return_value = mock_response

        # Call the method
        coin_data = self.api.coin_info('bitcoin')

        # Check if the response is as expected
        expected_data = mock.coins_id_response
        self.assertEqual(coin_data, expected_data)

    # ---------- /coins/{id}/tickers ---------- #
    @patch('requests.Session.get')
    def test_coin_market_tickers(self, mock_get):
        """Test getting tickers for a specific coin."""
        # Use the mock data from coins_id_tickers_mock.py
        mock_get.return_value.json.return_value = mock.coins_id_tickers_response

        # Call the method
        df = self.api.coin_market_tickers('bitcoin')

        # Convert the 'tickers' part of the mock response to a DataFrame for comparison
        expected_df = pd.DataFrame(mock.coins_id_tickers_response['tickers'])

        # Check if the response is as expected
        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/{id}/history ---------- #
    @patch('requests.Session.get')
    def test_coin_historical_on_date(self, mock_get):
        """Test fetching historical data for a specific coin on a given date."""
        # Use the mock data from coin_id_history_mock.py
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_history_response
        mock_get.return_value = mock_response

        # Call the method
        historical_data = self.api.coin_historical_on_date('bitcoin', '12-31-2022')

        # Check if the response is as expected
        expected_data = mock.coins_id_history_response
        self.assertEqual(historical_data, expected_data)

    # ---------- /coins/{id}/market_chart ---------- #
    @patch('requests.Session.get')
    def test_coin_historical_market_data_by_days(self, mock_get):
        """Test fetching historical market data for a specific coin."""
        # Use the mock data from coins_id_market_chart_mock.py
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_market_chart_response
        mock_get.return_value = mock_response

        # Call the method
        historical_data_df = self.api.coin_historical_market_data(coin_id='bitcoin', vs_currency='usd', days='max')

        # Check if the DataFrame has the expected columns
        expected_columns = ['price', 'market_cap', 'total_volume']
        self.assertListEqual(list(historical_data_df.columns), expected_columns)

    # ---------- coins/{coin_id}/market_chart/range ---------- #
    @patch('requests.Session.get')
    def test_coin_historical_market_data_by_dates(self, mock_get):
        """Test fetching historical market data for a specific coin."""
        # Use the mock data from coins_id_market_chart_mock.py
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_market_chart_range_response
        mock_get.return_value = mock_response

        # Call the method
        historical_data_df = self.api.coin_historical_market_data(
            'bitcoin',
            'usd',
            from_date='01-01-2023',
            to_date='12-31-2023'
        )

        # Check if the DataFrame has the expected columns
        expected_columns = ['price', 'market_cap', 'total_volume']
        self.assertListEqual(list(historical_data_df.columns), expected_columns)

    # ---------- /coins/{id}/market_chart for multiple tickers ---------- #
    @patch.object(CoinGeckoAPI, 'multiple_coins_ohlc_data')
    def test_multiple_coins_historical_data(self, mock_get):
        """Test fetching historical market data for multiple coins."""
        # Prepare mock response
        mock_data_df = pd.DataFrame({
            'timestamp': [item[0] for item in mock.coins_id_market_chart_response['prices']],
            'price': [item[1] for item in mock.coins_id_market_chart_response['prices']],
            'market_cap': [item[1] for item in mock.coins_id_market_chart_response['market_caps']],
            'total_volume': [item[1] for item in mock.coins_id_market_chart_response['total_volumes']]
        })

        # Mock the get_coin_historical_data method to return the same mock data for each coin
        mock_get.side_effect = [mock_data_df] * len(['bitcoin', 'ethereum', 'tether'])

        # Use the initialized API from setUp
        historical_data_dict = self.api.multiple_coins_historical_data(['bitcoin', 'ethereum', 'tether'])

        # Check the structure of the returned dictionary
        self.assertIn('price', historical_data_dict)
        self.assertIn('market_cap', historical_data_dict)
        self.assertIn('total_volume', historical_data_dict)

    # ---------- /coins/{id}/ohlc ---------- #
    @patch('requests.Session.get')
    def test_coin_ohlc_data(self, mock_get):
        """Test fetching OHLC data for a specific coin."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_ohlc_response
        mock_get.return_value = mock_response

        # Call the method
        ohlc_df = self.api.coin_ohlc_data('bitcoin')

        # Assert the DataFrame structure
        expected_columns = ['Open', 'High', 'Low', 'Close']
        self.assertListEqual(list(ohlc_df.columns), expected_columns)
        self.assertTrue(isinstance(ohlc_df.index, pd.DatetimeIndex))

        # Assert data correctness
        for i, row in enumerate(mock.coins_id_ohlc_response):
            self.assertEqual(ohlc_df.iloc[i]['Open'], row[1])
            self.assertEqual(ohlc_df.iloc[i]['High'], row[2])
            self.assertEqual(ohlc_df.iloc[i]['Low'], row[3])
            self.assertEqual(ohlc_df.iloc[i]['Close'], row[4])

    # ---------- /coins/{id}/ohlc?precision=2 ---------- #
    @patch('requests.Session.get')
    def test_coin_ohlc_data_with_precision(self, mock_get):
        """Test fetching OHLC data for a specific coin with precision."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_ohlc_response
        mock_get.return_value = mock_response

        # Call the method with precision
        precision = '2'  # example precision value
        ohlc_df = self.api.coin_ohlc_data('bitcoin', precision=precision)

        # Assert that the precision parameter was passed correctly
        args, kwargs = mock_get.call_args
        self.assertTrue('precision' in kwargs['params'])
        self.assertEqual(kwargs['params']['precision'], precision)

    # ---------- /coins/{id}/ohlc for multiple tickers ---------- #
    @patch.object(CoinGeckoAPI, 'coin_ohlc_data')
    def test_multiple_coins_ohlc_data(self, mock_get):
        """Test fetching OHLC data for multiple coins."""
        # Prepare the mock responses for each coin
        mock_get.side_effect = [
            pd.DataFrame(mock.coins_ids_ohlc_response['bitcoin'], columns=['Open', 'High', 'Low', 'Close']),
            pd.DataFrame(mock.coins_ids_ohlc_response['ethereum'], columns=['Open', 'High', 'Low', 'Close']),
            pd.DataFrame(mock.coins_ids_ohlc_response['tether'], columns=['Open', 'High', 'Low', 'Close']),
        ]

        # Call the method
        ohlc_data = self.api.multiple_coins_ohlc_data(['bitcoin', 'ethereum', 'tether'])

        # Assert the structure of the returned dictionary
        for key in ['Open', 'High', 'Low', 'Close']:
            self.assertIn(key, ohlc_data)
            self.assertTrue(isinstance(ohlc_data[key], pd.DataFrame))
            self.assertEqual(list(ohlc_data[key].columns), ['bitcoin', 'ethereum', 'tether'])

    # ---------- CONTRACT ---------- #

    # ---------- /coins/{id}/contract/{contract_address} ---------- #
    @patch('requests.Session.get')
    def test_coin_by_contract(self, mock_get):
        """Test fetching coin information using a specific contract address."""
        platform_id = "ethereum"
        contract_address = "0x5a98fcbea516cf06857215779fd812ca3bef1b32"

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_platform_id_contract_address_response
        mock_get.return_value = mock_response

        # Call the method
        response = self.api.coin_by_contract(platform_id, contract_address)

        # Assert the response is as expected
        self.assertEqual(response, mock.coins_platform_id_contract_address_response)

    # ---------- /coins/{id}/contract/{contract_address}/market_chart ---------- #
    # or
    # ---------- /coins/{id}/contract/{contract_address}/market_chart/range ---------- #
    @patch('requests.Session.get')
    def test_contract_historical_market_data_by_days_with_precision(self, mock_get):
        """Test fetching historical market data for a token from its contract address."""
        platform_id = "ethereum"
        contract_address = "0x5a98fcbea516cf06857215779fd812ca3bef1b32"
        vs_currency = "usd"
        days = "max"
        precision = "2"

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_contract_address_market_chart_response
        mock_get.return_value = mock_response

        # Call the method
        historical_data_df = self.api.contract_historical_market_data(
            platform_id,
            contract_address,
            vs_currency,
            days,
            precision=precision
        )

        # Check DataFrame structure
        expected_columns = ['price', 'market_cap', 'total_volume']
        self.assertListEqual(list(historical_data_df.columns), expected_columns)
        self.assertTrue(isinstance(historical_data_df.index, pd.DatetimeIndex))

        # Check data correctness (sample check for the first row)
        first_row = historical_data_df.iloc[0]
        mock_first_row = mock.coins_contract_address_market_chart_response['prices'][0]
        self.assertEqual(first_row['price'], mock_first_row[1])

        # Assert that the precision parameter was passed correctly
        args, kwargs = mock_get.call_args
        self.assertTrue('precision' in kwargs['params'])
        self.assertEqual(kwargs['params']['precision'], precision)

    # ---------- coins/{id}/contract/{contract_address}/market_chart ---------- #
    # or
    # ---------- coins/{id}/contract/{contract_address}/market_chart/range ---------- #
    @patch('requests.Session.get')
    def test_contract_historical_market_data_by_dates(self, mock_get):
        """Test fetching historical market data for a token from its contract address."""
        platform_id = "ethereum"
        contract_address = "0x5a98fcbea516cf06857215779fd812ca3bef1b32"
        vs_currency = "usd"

        # Convert the first and last timestamp in the mock response to datetime
        first_timestamp = 1702771200000  # First timestamp from mock data
        last_timestamp = 1703116800000  # Last timestamp from mock data
        from_date = pd.to_datetime(first_timestamp, unit='ms', utc=True).strftime('%m-%d-%Y')
        to_date = pd.to_datetime(last_timestamp, unit='ms', utc=True).strftime('%m-%d-%Y')

        # Mock response for the date range case
        mock_response_range = MagicMock()
        mock_response_range.json.return_value = mock.coins_contract_address_market_chart_range_response
        mock_get.return_value = mock_response_range

        # Call the method for the date range case
        historical_data_df_range = self.api.contract_historical_market_data(platform_id, contract_address, vs_currency,
                                                                            from_date=from_date, to_date=to_date)

        # Check DataFrame structure for the date range case
        expected_columns = ['price', 'market_cap', 'total_volume']
        self.assertListEqual(list(historical_data_df_range.columns), expected_columns)
        self.assertTrue(isinstance(historical_data_df_range.index, pd.DatetimeIndex))

        # Convert the from_date and to_date to timezone-aware (UTC) datetime objects
        start_date = utc.localize(datetime.strptime(from_date, "%m-%d-%Y"))
        end_date = utc.localize(datetime.strptime(to_date, "%m-%d-%Y"))

        # Check if date range filtering worked correctly
        self.assertTrue(all(start_date <= dt <= end_date for dt in historical_data_df_range.index))

    # ---------- ASSET PLATFORMS ---------- #

    # ---------- /asset_platforms ---------- #
    @patch('requests.Session.get')
    def test_asset_platforms_list(self, mock_get):
        """Test fetching all asset platforms without any filter."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.asset_platforms_response
        mock_get.return_value = mock_response

        # Call the method
        asset_platforms_df = self.api.asset_platforms_list()

        # Check if the DataFrame has the expected columns
        expected_columns = ['id', 'chain_identifier', 'name', 'shortname', 'native_coin_id']
        self.assertListEqual(list(asset_platforms_df.columns), expected_columns)

        # Check if the data matches the mock response
        for i, row in enumerate(mock.asset_platforms_response):
            for col in expected_columns:
                self.assertEqual(asset_platforms_df.iloc[i][col], row[col])

    # ---------- /asset_platforms?platform_filter=nft ---------- #
    @patch('requests.Session.get')
    def test_asset_platforms_list_with_platform_filter(self, mock_get):
        """Test fetching asset platforms with 'nft' filter."""
        # Mock the API response
        mock_response = MagicMock()
        # Assuming a different mock response for NFT filter
        mock_response.json.return_value = mock.filtered_asset_platforms_response
        mock_get.return_value = mock_response

        # Call the method with 'nft' filter
        asset_platforms_df = self.api.asset_platforms_list(platform_filter="nft")

        # Check if the DataFrame has the expected columns
        expected_columns = ['id', 'chain_identifier', 'name', 'shortname', 'native_coin_id']
        self.assertListEqual(list(asset_platforms_df.columns), expected_columns)

    # ---------- CATEGORIES ---------- #

    # ---------- /coins/categories/list ---------- #
    @patch('requests.Session.get')
    def test_cryptocurrency_categories_list(self, mock_get):
        """Test fetching a list of all cryptocurrency categories."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_categories_list_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.cryptocurrency_categories_list()

        # Check if the DataFrame is as expected
        expected_df = pd.DataFrame(mock.coins_categories_list_response)
        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- /coins/categories ---------- #
    @patch('requests.Session.get')
    def test_categories_market_data(self, mock_get):
        """Test fetching a list of all cryptocurrency categories with market data."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_categories_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.categories_market_data(order='market_cap_desc')

        # Check if the DataFrame is as expected
        expected_df = pd.DataFrame(mock.coins_categories_response)
        pd.testing.assert_frame_equal(df, expected_df)

    # ---------- EXCHANGES ---------- #

    # ---------- /exchanges ---------- #
    @patch('requests.Session.get')
    def test_active_exchanges_list(self, mock_get):
        """Test fetching a list of all active exchanges with trading volumes."""
        per_page = 100
        page = 1

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchanges_response
        mock_get.return_value = mock_response

        # Call the method
        active_exchanges_df = self.api.active_exchanges_list(per_page=per_page, page=page)

        # Check if the DataFrame has the expected columns
        expected_columns = ['id', 'name', 'year_established', 'country', 'description', 'url', 'image',
                            'has_trading_incentive', 'trust_score', 'trust_score_rank',
                            'trade_volume_24h_btc', 'trade_volume_24h_btc_normalized']
        self.assertListEqual(list(active_exchanges_df.columns), expected_columns)

        # Check if the data matches the mock response
        for i, row in enumerate(mock.exchanges_response):
            for col in expected_columns:
                self.assertEqual(active_exchanges_df.iloc[i][col], row[col])

    # ---------- /exchanges/list ---------- #
    @patch('requests.Session.get')
    def test_all_exchanges_list(self, mock_get):
        """Test fetching a list of all supported market IDs and names."""

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchanges_list_response
        mock_get.return_value = mock_response

        # Call the method
        supported_exchanges_df = self.api.all_exchanges_list()

        # Check if the DataFrame has the expected columns
        expected_columns = ['id', 'name']
        self.assertListEqual(list(supported_exchanges_df.columns), expected_columns)

        # Check if the data matches the mock response
        for i, row in enumerate(mock.exchanges_list_response):
            self.assertEqual(supported_exchanges_df.iloc[i]['id'], row['id'])
            self.assertEqual(supported_exchanges_df.iloc[i]['name'], row['name'])

    # ---------- /exchanges/{id} ---------- #
    @patch('requests.Session.get')
    def test_exchange_volume_data(self, mock_get):
        exchange_id = "binance"

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchanges_id_response
        mock_get.return_value = mock_response

        # Call the method
        exchange_volume_data = self.api.exchange_volume_data(exchange_id)

        # Check if the data contains the expected keys
        expected_keys = ['trade_volume_24h_btc', 'tickers']
        for key in expected_keys:
            self.assertIn(key, exchange_volume_data)

        # Check if the trade volume matches the mock response
        self.assertEqual(exchange_volume_data['trade_volume_24h_btc'],
                         mock.exchanges_id_response['trade_volume_24h_btc'])

        # Check if the tickers data matches the mock response
        self.assertEqual(len(exchange_volume_data['tickers']),
                         len(mock.exchanges_id_response['tickers']))

        # Optionally, further check the contents of the tickers data
        for idx, ticker in enumerate(exchange_volume_data['tickers']):
            self.assertEqual(ticker, mock.exchanges_id_response['tickers'][idx])

    # ---------- /exchanges/{id}/tickers ---------- #
    @patch('requests.Session.get')
    def test_exchange_market_tickers(self, mock_get):
        """Test fetching paginated tickers for a specific exchange."""
        exchange_id = "gdax"
        coin_ids = None  # or a string of comma-separated coin IDs
        include_exchange_logo = "false"
        page = 1
        depth = "false"
        order = "trust_score_desc"

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchanges_id_tickers_response
        mock_get.return_value = mock_response

        # Call the method
        exchange_tickers_df = self.api.exchange_market_tickers(exchange_id, coin_ids, include_exchange_logo, page,
                                                               depth, order)

        # Check if the DataFrame has the expected data
        expected_columns = ['base', 'target', 'market', 'last', 'volume', 'converted_last', 'converted_volume',
                            'trust_score', 'bid_ask_spread_percentage', 'timestamp', 'last_traded_at',
                            'last_fetch_at', 'is_anomaly', 'is_stale', 'trade_url', 'token_info_url',
                            'coin_id', 'target_coin_id']
        self.assertListEqual(list(exchange_tickers_df.columns), expected_columns)

        # Check the content of the DataFrame against the mock response
        self.assertEqual(len(exchange_tickers_df), len(mock.exchanges_id_tickers_response['tickers']))
        self.assertEqual(exchange_tickers_df['base'].iloc[0], mock.exchanges_id_tickers_response['tickers'][0]['base'])

    # ---------- /exchanges/{id}/volume_chart ---------- #
    @patch('requests.Session.get')
    def test_exchange_historical_volume(self, mock_get):
        """Test fetching historical volume data for an exchange."""
        exchange_id = "binance"
        days = 5

        # Setup mock response for rolling volume data
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchanges_id_volume_chart_response
        mock_get.return_value = mock_response

        # Call the method for rolling volume data
        exchange_volume_chart_df = self.api.exchange_historical_volume(exchange_id, days)

        # Verify DataFrame structure and data for rolling volume data
        self.assertIsInstance(exchange_volume_chart_df, pd.DataFrame)
        self.assertTrue('volume' in exchange_volume_chart_df.columns)

        # Additional tests for rolling volume data...

        # Setup mock response for historical volume data
        from_date = "01-01-2022"
        to_date = "01-31-2022"
        mock_get.return_value = mock_response  # Reuse mock response

        # Call the method for historical volume data
        exchange_volume_chart_df = self.api.exchange_historical_volume(exchange_id, from_date=from_date,
                                                                       to_date=to_date)

        # Verify DataFrame structure and data for historical volume data
        self.assertIsInstance(exchange_volume_chart_df, pd.DataFrame)
        self.assertTrue('volume' in exchange_volume_chart_df.columns)

    def test_exchange_historical_volume_date_range_error(self):
        """Test date range error in exchange_historical_volume."""
        exchange_id = "binance"
        from_date = "01-01-2022"
        to_date = "02-02-2022"  # 32 days, exceeding the limit

        with self.assertRaises(ValueError):
            self.api.exchange_historical_volume(exchange_id, from_date=from_date, to_date=to_date)

    # ---------- DERIVATIVES ---------- #

    # ---------- /derivatives ---------- #
    @patch('requests.Session.get')
    def test_derivatives_market_tickers(self, mock_get):
        """Test fetching a list of all derivative tickers."""

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.derivatives_response
        mock_get.return_value = mock_response

        # Call the method
        derivatives_df = self.api.derivatives_market_tickers()

        # Verify DataFrame structure and content
        self.assertIsInstance(derivatives_df, pd.DataFrame)
        expected_columns = ['market', 'symbol', 'index_id', 'price', 'price_percentage_change_24h', 'contract_type',
                            'index', 'basis', 'spread', 'funding_rate', 'open_interest', 'volume_24h',
                            'last_traded_at', 'expired_at']
        self.assertListEqual(list(derivatives_df.columns), expected_columns)

        # Verify data content of DataFrame
        for i, row in enumerate(mock.derivatives_response):
            for col in expected_columns:
                self.assertEqual(derivatives_df.iloc[i][col], row[col])

    # ---------- /derivatives/exchanges ---------- #
    @patch('requests.Session.get')
    def test_derivatives_exchanges_list(self, mock_get):
        """Test fetching a list of all derivative exchanges."""

        # Set up parameters for the test
        order = "name_asc"
        per_page = 50
        page = 2

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.derivatives_exchanges_response
        mock_get.return_value = mock_response

        # Call the method
        derivatives_exchanges_df = self.api.derivatives_exchanges_list(order=order, per_page=per_page, page=page)

        # Verify DataFrame structure and content
        self.assertIsInstance(derivatives_exchanges_df, pd.DataFrame)
        expected_columns = ['name', 'id', 'open_interest_btc', 'trade_volume_24h_btc', 'number_of_perpetual_pairs',
                            'number_of_futures_pairs', 'image', 'year_established', 'country', 'description', 'url']
        self.assertListEqual(list(derivatives_exchanges_df.columns), expected_columns)

        # Verify data content of DataFrame
        for i, row in enumerate(mock.derivatives_exchanges_response):
            for col in expected_columns:
                self.assertEqual(derivatives_exchanges_df.iloc[i][col], row[col])

    # ---------- /derivatives/exchanges/{id} ---------- #
    @patch('requests.Session.get')
    def test_derivatives_exchange_info(self, mock_get):
        """Test fetching detailed data for a specific derivative exchange."""

        # Set up parameters for the test
        exchange_id = "bitmex"
        include_tickers = "all"

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.derivatives_exchanges_id_response
        mock_get.return_value = mock_response

        # Call the method
        derivatives_exchange_data_df = self.api.derivatives_exchange_info(exchange_id, include_tickers)

        # Verify DataFrame structure and content
        self.assertIsInstance(derivatives_exchange_data_df, pd.DataFrame)
        expected_columns = ['Attribute', 'Value']
        self.assertListEqual(list(derivatives_exchange_data_df.columns), expected_columns)

        # Verify data content of DataFrame
        for attr, value in mock.derivatives_exchanges_id_response.items():
            self.assertIn(attr, derivatives_exchange_data_df['Attribute'].values)
            self.assertIn(value, derivatives_exchange_data_df['Value'].values)

    # ---------- /derivatives/exchanges/list ---------- #
    @patch('requests.Session.get')
    def test_all_derivatives_exchanges_list(self, mock_get):
        """Test fetching a list of all derivative exchanges names and identifiers."""

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.derivatives_exchanges_list_response
        mock_get.return_value = mock_response

        # Call the method
        derivatives_exchanges_list_df = self.api.all_derivatives_exchanges_list()

        # Verify DataFrame structure and content
        self.assertIsInstance(derivatives_exchanges_list_df, pd.DataFrame)
        expected_columns = ['id', 'name']
        self.assertListEqual(list(derivatives_exchanges_list_df.columns), expected_columns)

        # Verify each item in the DataFrame matches the mock response
        for item in mock.derivatives_exchanges_list_response:
            self.assertIn(item['id'], derivatives_exchanges_list_df['id'].values)
            self.assertIn(item['name'], derivatives_exchanges_list_df['name'].values)

    # ---------- NFTs (beta) ---------- #

    # ---------- /nfts/list ---------- #
    @patch('requests.Session.get')
    def test_nfts_supported(self, mock_get):
        """Test fetching a list of all supported NFT ids."""

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_list_response
        mock_get.return_value = mock_response

        # Call the method
        supported_nfts_df = self.api.nfts_supported()

        # Verify DataFrame structure and content
        self.assertIsInstance(supported_nfts_df, pd.DataFrame)
        expected_columns = ['id', 'contract_address', 'name', 'asset_platform_id', 'symbol']
        self.assertListEqual(list(supported_nfts_df.columns), expected_columns)

        # Verify each item in the DataFrame matches the mock response
        for i, item in supported_nfts_df.iterrows():
            self.assertEqual(item['id'], mock.nfts_list_response[i]['id'])
            self.assertEqual(item['contract_address'], mock.nfts_list_response[i]['contract_address'])
            self.assertEqual(item['name'], mock.nfts_list_response[i]['name'])
            self.assertEqual(item['asset_platform_id'], mock.nfts_list_response[i]['asset_platform_id'])
            self.assertEqual(item['symbol'], mock.nfts_list_response[i]['symbol'])

    # ---------- /nfts/{id} ---------- #
    @patch('requests.Session.get')
    def test_nft_collection_info(self, mock_get):
        """Test fetching current data for a specific NFT collection."""

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_id_response
        mock_get.return_value = mock_response

        # Call the method with an example nft_id
        nft_id = "bored-ape-yacht-club"
        nft_collection_df = self.api.nft_collection_info(nft_id)

        # Verify DataFrame structure
        self.assertIsInstance(nft_collection_df, pd.DataFrame)
        self.assertTrue(nft_id == nft_collection_df.index[0])

        # Since there's only one row, get that row for comparison
        nft_collection_data = nft_collection_df.iloc[0]

        # Verify content matches the mock response
        for key, value in mock.nfts_id_response.items():
            # Skip 'id' as it's the DataFrame's index
            if key == 'id':
                continue

            # Handle dictionary type values properly
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Access nested dictionary data correctly
                    self.assertEqual(nft_collection_data[key][sub_key], sub_value)
            else:
                # For non-dictionary type values, directly compare the value
                self.assertEqual(nft_collection_data[key], value)

    # ---------- /nfts/{asset_platform_id}/contract/{contract_address} ---------- #
    @patch('requests.Session.get')
    def test_nft_collection_info_by_platform_and_contract(self, mock_get):
        """Test fetching current data for a specific NFT collection using asset platform ID and contract address."""

        # Setup mock response for asset platform ID and contract address
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_platform_contract_response
        mock_get.return_value = mock_response

        # Call the method with example asset platform ID and contract address
        asset_platform_id = "ethereum"
        contract_address = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"
        nft_collection_df = self.api.nft_collection_info(asset_platform_id=asset_platform_id,
                                                         contract_address=contract_address)

        # Add assertions to ensure the mock was called with the correct endpoint
        expected_endpoint = f'nfts/{asset_platform_id}/contract/{contract_address}'
        args, kwargs = mock_get.call_args
        self.assertIn(expected_endpoint, args[0])

        # Verify DataFrame structure
        self.assertIsInstance(nft_collection_df, pd.DataFrame)
        self.assertTrue('id' in nft_collection_df.index.name)  # Verify 'id' is the index name

        # Verify the index value matches the expected 'id'
        expected_id = mock.nfts_platform_contract_response.get('id', '')
        self.assertEqual(nft_collection_df.index[0], expected_id)

        # Since there's only one row, get that row for comparison
        nft_collection_data = nft_collection_df.iloc[0]

        # Verify content matches the mock response
        for key, value in mock.nfts_platform_contract_response.items():
            if key == 'id':
                continue  # Skip 'id' as it's the DataFrame's index

            # Handle dictionary type values properly
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Access nested dictionary data correctly
                    self.assertEqual(nft_collection_data[key][sub_key], sub_value)
            else:
                # For non-dictionary type values, directly compare the value
                self.assertEqual(nft_collection_data[key], value)

    @patch('requests.Session.get')
    def test_nft_collection_info_invalid_arguments(self, mock_get):
        """Test fetching NFT collection data with invalid arguments."""
        with self.assertRaises(ValueError):
            # Call without necessary arguments
            self.api.nft_collection_info()

        # Verify that the API was not called
        mock_get.assert_not_called()

    # ---------- /nfts/{id} for multiple coin ids ---------- #
    @patch('pycgapi.CoinGeckoAPI.nft_collection_info')
    def test_nft_collections_info(self, mock_nft_collection_info):
        """Test fetching current data for multiple NFT collections."""

        # Mock responses for each NFT ID
        nft_ids = ['galxe-oat-v2', 'cryptopunks', 'cometh-spaceships', 'bored-ape-yacht-club', 'yuliorigingenone']
        mock_responses = {
            'galxe-oat-v2': mock.galxe_oat_v2_response,
            'cryptopunks': mock.cryptopunks_response,
            'cometh-spaceships': mock.cometh_spaceships_response,
            'bored-ape-yacht-club': mock.bored_ape_yacht_club_response,
            'yuliorigingenone': mock.yuliorigingenone_response
        }

        # Configure the mock to return a DataFrame for each ID in the list
        mock_nft_collection_info.side_effect = lambda *args, **kwargs: pd.DataFrame([mock_responses[kwargs['nft_id']]])

        # Test with nft_ids
        multiple_nft_collections_df = self.api.nft_collections_info(nft_ids=nft_ids)

        # Verify DataFrame structure and content for nft_ids
        self.assertIsInstance(multiple_nft_collections_df, pd.DataFrame)
        self.assertEqual(len(multiple_nft_collections_df), len(nft_ids))
        for i, nft_id in enumerate(nft_ids):
            nft_data = multiple_nft_collections_df.iloc[i].to_dict()
            for key, expected_value in mock_responses[nft_id].items():
                self.assertEqual(nft_data.get(key), expected_value)

        # Test with asset_platform_id and contract_addresses
        asset_platform_id = 'ethereum'
        contract_addresses = [
            '0x5d666f215a85b87cb042d59662a7ecd2c8cc44e6',
            '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB',
            '0xbcd4f1ecff4318e7a0c791c7728f3830db506c71',
            '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
            '0x735c4a681f1649f5eee8aac871aa1d89ff056217'
        ]
        mock_responses = {
            '0x5d666f215a85b87cb042d59662a7ecd2c8cc44e6': mock.galxe_oat_v2_response,
            '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB': mock.cryptopunks_response,
            '0xbcd4f1ecff4318e7a0c791c7728f3830db506c71': mock.cometh_spaceships_response,
            '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d': mock.bored_ape_yacht_club_response,
            '0x735c4a681f1649f5eee8aac871aa1d89ff056217': mock.yuliorigingenone_response
        }

        mock_nft_collection_info.side_effect = lambda *args, **kwargs: pd.DataFrame(
            [mock_responses[kwargs['contract_address']]])
        multiple_nft_collections_df = self.api.nft_collections_info(asset_platform_id=asset_platform_id,
                                                                    contract_addresses=contract_addresses)

        # Verify DataFrame structure and content for asset_platform_id and contract_addresses
        self.assertIsInstance(multiple_nft_collections_df, pd.DataFrame)
        self.assertEqual(len(multiple_nft_collections_df), len(contract_addresses))

        # Test ValueError for invalid arguments
        with self.assertRaises(ValueError):
            self.api.nft_collections_info()

    @patch('pycgapi.CoinGeckoAPI.nft_collection_info')
    def test_nft_collections_info_with_empty_data(self, mock_nft_collection_info):
        """Test fetching current data for multiple NFT collections with no valid data."""

        # Mock responses for each NFT ID
        nft_ids = ['invalid-nft1', 'invalid-nft2']
        mock_responses = {
            'invalid-nft1': {},  # Empty dict to simulate no data
            'invalid-nft2': {}  # Empty dict to simulate no data
        }

        # Configure the mock to return an empty DataFrame for each invalid ID
        mock_nft_collection_info.side_effect = lambda *args, **kwargs: pd.DataFrame(
            [mock_responses.get(kwargs['nft_id'], {})])

        # Test with invalid nft_ids
        empty_nft_collections_df = self.api.nft_collections_info(nft_ids=nft_ids)

        # Verify that the resulting DataFrame is empty
        self.assertTrue(empty_nft_collections_df.empty)

    # ---------- EXCHANGE RATES ---------- #

    # ---------- /exchange_rates ---------- #
    @patch('requests.get')
    def test_btc_exchange_rates(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.exchange_rates_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.btc_exchange_rates()

        # Test that the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test that the DataFrame has the expected columns
        expected_columns = ['name', 'unit', 'value', 'type']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test a few values from the DataFrame
        # Assuming that 'btc', 'eth', and 'usd' are always present in the response
        btc_row = df.loc['btc']
        eth_row = df.loc['eth']
        usd_row = df.loc['usd']

        self.assertEqual(btc_row['name'], "Bitcoin")
        self.assertEqual(btc_row['unit'], "BTC")
        self.assertEqual(btc_row['value'], 1)
        self.assertEqual(btc_row['type'], "crypto")

        self.assertEqual(eth_row['name'], "Ether")
        self.assertEqual(eth_row['unit'], "ETH")

        self.assertEqual(usd_row['name'], "US Dollar")
        self.assertEqual(usd_row['unit'], "$")

    # ---------- SEARCH ---------- #

    # ---------- /search ---------- #
    @patch('requests.Session.get')
    def test_search_coingecko(self, mock_get):
        """Test searching for coins, exchanges, NFTs, and more."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.search_response
        mock_get.return_value = mock_response

        # Call the method
        search_result = self.api.search_coingecko('solana')

        # Check if the response contains the 'coins' key and its value is a DataFrame
        self.assertIn('coins', search_result)
        self.assertIsInstance(search_result['coins'], pd.DataFrame)

        # Extract the DataFrame for further validation
        df = search_result['coins']

        # Check if the DataFrame has the expected columns
        expected_columns = ['id', 'name', 'api_symbol', 'symbol', 'market_cap_rank', 'thumb', 'large']
        self.assertListEqual(list(df.columns), expected_columns)

        # Check if the data matches the mock response
        for i, row in enumerate(mock.search_response['coins']):
            for col in expected_columns:
                self.assertEqual(df.iloc[i][col], row[col])

    # ---------- TRENDING ---------- #

    # ---------- /search/trending ---------- #
    @patch('requests.Session.get')
    def test_trending_searches(self, mock_get):
        """Test fetching trending search terms."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.search_trending_response
        mock_get.return_value = mock_response

        # Call the method
        trending_searches = self.api.trending_searches()

        # Expected columns
        expected_columns = ['id', 'coin_id', 'name', 'symbol', 'market_cap_rank', 'thumb', 'small', 'large', 'slug',
                            'price_btc', 'score', 'data']
        self.assertListEqual(list(trending_searches.columns), expected_columns)

    # ---------- GLOBAL ---------- #

    # ---------- /global ---------- #
    @patch('requests.Session.get')
    def test_global_crypto_stats(self, mock_get):
        """Test fetching global data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.global_response
        mock_get.return_value = mock_response

        # Call the method
        global_data = self.api.global_crypto_stats()

        # Ensure the returned object is a tuple of four DataFrames
        self.assertIsInstance(global_data, tuple)
        self.assertEqual(len(global_data), 4)
        for df in global_data:
            self.assertIsInstance(df, pd.DataFrame)

        # Test the structure and content of each DataFrame
        df, market_cap_percentage, total_market_cap, total_volume = global_data

        # Test the main DataFrame
        expected_main_index = ['active_cryptocurrencies', 'ended_icos', 'market_cap_change_percentage_24h_usd',
                               'market_cap_percentage', 'markets', 'ongoing_icos', 'total_market_cap',
                               'total_volume', 'upcoming_icos', 'updated_at']
        self.assertListEqual(list(df.index), expected_main_index)
        self.assertEqual(df.loc['active_cryptocurrencies', 'data'], 11826)  # Example value check

        # Test market_cap_percentage DataFrame
        expected_market_cap_columns = ['market_cap_percentage']
        self.assertListEqual(list(market_cap_percentage.columns), expected_market_cap_columns)
        self.assertIn('btc', market_cap_percentage.index)  # Check if 'btc' is a row index

        # Test total_market_cap DataFrame
        expected_total_market_cap_columns = ['total_market_cap']
        self.assertListEqual(list(total_market_cap.columns), expected_total_market_cap_columns)
        self.assertIn('btc', total_market_cap.index)  # Check if 'btc' is a row index

        # Test total_volume DataFrame
        expected_total_volume_columns = ['total_volume']
        self.assertListEqual(list(total_volume.columns), expected_total_volume_columns)
        self.assertIn('btc', total_volume.index)  # Check if 'btc' is a row index

    # ---------- /global/decentralized_finance_defi ---------- #
    @patch('requests.Session.get')
    def test_global_defi_stats(self, mock_get):
        """Test fetching global DeFi data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.global_defi_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.global_defi_stats()

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure and content of the DataFrame
        expected_index = ['defi_dominance', 'defi_market_cap', 'defi_to_eth_ratio', 'eth_market_cap',
                          'top_coin_defi_dominance', 'top_coin_name', 'trading_volume_24h']
        self.assertListEqual(list(df.index), expected_index)

        # Test if the DataFrame contains the expected values from the mock response
        expected_values = mock.global_defi_response['data']
        for idx in expected_index:
            self.assertEqual(df.loc[idx].squeeze(), expected_values[idx])  # Ensure the values match

    # ---------- COMPANIES (beta) ---------- #

    # ---------- /companies/public_treasury/{coin_id} ---------- #
    @patch('requests.Session.get')
    def test_companies_holdings(self, mock_get):
        """Test fetching public companies' Bitcoin or Ethereum holdings."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.companies_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.companies_holdings()

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure and content of the DataFrame
        expected_columns = ['name', 'symbol', 'country', 'total_holdings',
                            'total_entry_value_usd', 'total_current_value_usd',
                            'percentage_of_total_supply']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test if the DataFrame contains the expected values from the mock response
        for i, company_data in enumerate(mock.companies_response['companies']):
            for col in expected_columns:
                self.assertEqual(df.iloc[i][col], company_data[col])  # Ensure the values match

    # ---------- PAID PLAN ENDPOINTS ---------- #

    # ---------- /coins/list/new ---------- #
    @patch('requests.Session.get')
    def test_new_coins_listed(self, mock_get):
        """Test fetching the latest 200 coins recently listed on CoinGecko."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_list_new_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.new_coins_listed()

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure and content of the DataFrame
        expected_columns = ['id', 'symbol', 'name', 'activated_at']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test if the DataFrame contains the expected values from the mock response
        for i, coin_data in enumerate(mock.coins_list_new_response):
            for col in expected_columns:
                self.assertEqual(df.iloc[i][col], coin_data[col])  # Ensure the values match

        # Optionally, check the number of rows to match the mock response length
        self.assertEqual(len(df), len(mock.coins_list_new_response))

    # ---------- /coins/top_gainers_losers ---------- #
    @patch('requests.Session.get')
    def test_gainers_losers(self, mock_get):
        """Test fetching the top gainers and losers."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.top_gainers_losers_response
        mock_get.return_value = mock_response

        # Call the method
        gainers, losers = self.api.gainers_losers(vs_currency='usd', duration='1h', top_coins=300)

        # Ensure the returned objects are DataFrames
        self.assertIsInstance(gainers, pd.DataFrame)
        self.assertIsInstance(losers, pd.DataFrame)

        # Test the structure and content of the gainers DataFrame
        expected_gainers_columns = ['id', 'symbol', 'name', 'image', 'market_cap_rank', 'usd', 'usd_24h_vol',
                                    'usd_1h_change']
        self.assertListEqual(list(gainers.columns), expected_gainers_columns)

        # Test if the gainers DataFrame contains the expected values from the mock response
        for i, gainer_data in enumerate(mock.top_gainers_losers_response['top_gainers']):
            for col in expected_gainers_columns:
                self.assertEqual(gainers.iloc[i][col], gainer_data[col])

        # Test the structure and content of the losers DataFrame
        expected_losers_columns = ['id', 'symbol', 'name', 'image', 'market_cap_rank', 'usd', 'usd_24h_vol',
                                   'usd_1h_change']
        self.assertListEqual(list(losers.columns), expected_losers_columns)

        # Test if the losers DataFrame contains the expected values from the mock response
        for i, loser_data in enumerate(mock.top_gainers_losers_response['top_losers']):
            for col in expected_losers_columns:
                self.assertEqual(losers.iloc[i][col], loser_data[col])

    # ---------- /global/market_cap_chart ---------- #
    @patch('requests.Session.get')
    def test_historical_global_market_cap(self, mock_get):
        """Test fetching historical global market cap and volume data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.market_cap_chart_response
        mock_get.return_value = mock_response

        # Call the method
        market_cap_df, volume_df = self.api.historical_global_market_cap(days='max', vs_currency='usd')

        # Ensure the returned objects are DataFrames
        self.assertIsInstance(market_cap_df, pd.DataFrame)
        self.assertIsInstance(volume_df, pd.DataFrame)

        # Test the structure and content of the market_cap DataFrame
        expected_market_cap_columns = ['market_cap']
        self.assertListEqual(list(market_cap_df.columns), expected_market_cap_columns)

        # Check if the timestamps have been correctly converted to datetime and set as index
        self.assertTrue(isinstance(market_cap_df.index, pd.DatetimeIndex))

        # Test if the market_cap DataFrame contains the expected values from the mock response
        for i, (timestamp, market_cap) in enumerate(mock.market_cap_chart_response['market_cap_chart']['market_cap']):
            self.assertEqual(market_cap_df.iloc[i]['market_cap'], market_cap)

        # Test the structure and content of the volume DataFrame
        expected_volume_columns = ['volume']
        self.assertListEqual(list(volume_df.columns), expected_volume_columns)

        # Check if the timestamps have been correctly converted to datetime and set as index
        self.assertTrue(isinstance(volume_df.index, pd.DatetimeIndex))

        # Test if the volume DataFrame contains the expected values from the mock response
        for i, (timestamp, volume) in enumerate(mock.market_cap_chart_response['market_cap_chart']['volume']):
            self.assertEqual(volume_df.iloc[i]['volume'], volume)

    # ---------- /nfts/market ---------- #
    @patch('requests.Session.get')
    def test_nft_market_data(self, mock_get):
        """Test fetching NFT market data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_market_response
        mock_get.return_value = mock_response

        # Call the method
        df = self.api.nft_market_data()

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure of the DataFrame
        expected_columns = ['id', 'contract_address', 'asset_platform_id', 'name', 'image', 'description',
                            'native_currency', 'floor_price', 'market_cap', 'volume_24h',
                            'floor_price_in_usd_24h_percentage_change', 'number_of_unique_addresses',
                            'number_of_unique_addresses_24h_percentage_change', 'total_supply']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test the data types of certain columns
        self.assertTrue(df['id'].dtype == object)
        self.assertTrue(df['native_currency'].dtype == object)
        self.assertTrue(isinstance(df['floor_price'][0], dict))
        self.assertTrue(isinstance(df['market_cap'][0], dict))
        self.assertTrue(isinstance(df['volume_24h'][0], dict))

        # Check if the data matches the mock response
        for i, expected_row in enumerate(mock.nfts_market_response):
            for col in expected_columns:
                if col in ['floor_price', 'market_cap', 'volume_24h']:
                    self.assertDictEqual(df.iloc[i][col], expected_row[col])
                else:
                    self.assertEqual(df.iloc[i][col], expected_row[col])

    # ---------- nfts/{id}/market_chart ---------- #
    # or
    # ---------- nfts/{asset_platform_id}/contract/{contract_address}/market_chart ---------- #
    @patch('requests.Session.get')
    def test_nft_historical_data(self, mock_get):
        """Test fetching historical market data of a specific NFT collection."""

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_id_market_chart_response
        mock_get.return_value = mock_response

        # Test with nft_id
        nft_id = "bored-ape-yacht-club"
        df = self.api.nft_historical_data(nft_id, '30d')
        self.validate_nft_historical_data(df)

        # Test with asset_platform_id and contract_address
        asset_platform_id = 'ethereum'
        contract_address = '0x1234567890abcdef'
        df = self.api.nft_historical_data(asset_platform_id=asset_platform_id, contract_address=contract_address,
                                          days='30d')
        self.validate_nft_historical_data(df)

        # Test ValueError for invalid arguments
        with self.assertRaises(ValueError):
            self.api.nft_historical_data()

    def validate_nft_historical_data(self, df):
        """Helper function to validate the DataFrame."""
        self.assertIsInstance(df, pd.DataFrame)
        expected_columns = ['floor_price_usd', 'floor_price_native', 'h24_volume_usd', 'h24_volume_native',
                            'market_cap_usd', 'market_cap_native']
        self.assertListEqual(list(df.columns), expected_columns)

        for col in expected_columns:
            self.assertTrue(df[col].dtype == 'float64' or df[col].dtype == 'object')

        # Check if the data matches the mock response for a specific timestamp
        timestamp = pd.to_datetime(1666829111000, unit='ms')
        for col in expected_columns:
            expected_value = mock.nfts_id_market_chart_response[col][0][1]  # The second value of the first entry
            self.assertAlmostEqual(df.at[timestamp, col], expected_value, places=2)

    # ---------- nfts/{id}/tickers ---------- #
    @patch('requests.Session.get')
    def test_nft_market_tickers(self, mock_get):
        """Test fetching the latest floor price and 24h volume of an NFT collection on each NFT marketplace."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.nfts_id_tickers_response
        mock_get.return_value = mock_response

        # Assume the existence of an API class and method
        nft_id = "bored-ape-yacht-club"
        df = self.api.nft_market_tickers(nft_id)

        # Assertions
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['floor_price_in_native_currency', 'h24_volume_in_native_currency', 'native_currency',
                            'updated_at', 'nft_marketplace_id']
        assert list(df.columns) == expected_columns
        for col in expected_columns:
            assert df[col].dtype in ['float64', 'object']

        # Check data accuracy
        for i, ticker in enumerate(mock_response.json()['tickers']):
            for col in expected_columns:
                expected_value = ticker[col]
                if col in ['floor_price_in_native_currency', 'h24_volume_in_native_currency']:
                    assert abs(df.iloc[i][col] - expected_value) < 1e-2
                else:
                    assert df.iloc[i][col] == expected_value

    # ---------- ENTERPRISE PLAN ENDPOINTS ---------- #

    # ---------- /coins/{id}/circulating_supply_chart ---------- #
    @patch('requests.Session.get')
    def test_coin_circulating_supply_history(self, mock_get):
        """Test fetching historical circulating supply data for a coin using default settings."""
        # Mock the API response for default range
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_circulating_supply_chart_response
        mock_get.return_value = mock_response

        # Call the method for default range
        coin_id = 'bitcoin'  # Replace with the actual coin ID for a real test
        df_default = self.api.coin_circulating_supply_history(coin_id)

        # Validate default range test
        self.validate_circulating_supply_dataframe(df_default, mock.coins_id_circulating_supply_chart_response)

    # ---------- /coins/{id}/circulating_supply_chart/range ---------- #
    @patch('requests.Session.get')
    def test_coin_circulating_supply_history_with_dates(self, mock_get):
        """Test fetching historical circulating supply data for a coin within a specified date range."""
        # Mock the API response for specified date range
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_circulating_supply_chart_range_response
        mock_get.return_value = mock_response

        # Call the method for a specified date range
        coin_id = 'bitcoin'  # Replace with the actual coin ID for a real test
        df_range = self.api.coin_circulating_supply_history(coin_id, from_date='12-31-2022', to_date='12-31-2023')

        # Validate date range test
        self.validate_circulating_supply_dataframe(df_range, mock.coins_id_circulating_supply_chart_range_response)

    def validate_circulating_supply_dataframe(self, df, mock_response):
        """Helper method to validate the structure and data of the circulating supply DataFrame."""
        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure of the DataFrame
        expected_columns = ['circulating_supply']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test the data types of the DataFrame columns
        self.assertTrue(df.index.dtype == '<M8[ns]')  # '<M8[ns]' is numpy's datetime64
        df['circulating_supply'] = df['circulating_supply'].astype(float)  # Convert to float
        self.assertTrue(df['circulating_supply'].dtype == 'float64')

        # Check if the data matches the mock response for a specific timestamp
        timestamp = pd.to_datetime(mock_response['circulating_supply'][0][0], unit='ms')
        expected_supply = float(mock_response['circulating_supply'][0][1])
        self.assertAlmostEqual(df.at[timestamp, 'circulating_supply'], expected_supply, places=2)

    # ---------- /coins/{id}/total_supply_chart ---------- #
    @patch('requests.Session.get')
    def test_coin_total_supply_history(self, mock_get):
        """Test fetching historical total supply data for a coin."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_total_supply_chart_response
        mock_get.return_value = mock_response

        # Call the method
        coin_id = 'bitcoin'  # Replace with the actual coin ID for a real test
        df = self.api.coin_total_supply_history(coin_id)

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure of the DataFrame
        expected_columns = ['total_supply']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test the data types of the DataFrame columns
        self.assertTrue(df.index.dtype == '<M8[ns]')  # '<M8[ns]' is numpy's datetime64
        df['total_supply'] = df['total_supply'].astype(float)  # Convert to float
        self.assertTrue(df['total_supply'].dtype == 'float64')

        # Check if the data matches the mock response for a specific timestamp
        timestamp = pd.to_datetime(1702252800000, unit='ms')
        expected_supply = float(mock_response.json()['total_supply'][0][1])
        self.assertAlmostEqual(df.at[timestamp, 'total_supply'], expected_supply, places=2)

    # ---------- /coins/{id}/total_supply_chart/range ---------- #
    @patch('requests.Session.get')
    def test_coin_total_supply_history_with_date_range(self, mock_get):
        """Test fetching historical total supply data for a coin within a specific date range."""

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.coins_id_total_supply_chart_response
        mock_get.return_value = mock_response

        # Call the method with date range
        coin_id = 'bitcoin'  # Example coin ID
        from_date = '01-01-2023'
        to_date = '12-31-2023'
        df = self.api.coin_total_supply_history(coin_id, from_date=from_date, to_date=to_date)

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure of the DataFrame
        expected_columns = ['total_supply']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test the data types of the DataFrame columns
        self.assertTrue(df.index.dtype == '<M8[ns]')  # '<M8[ns]' is numpy's datetime64
        df['total_supply'] = df['total_supply'].astype(float)  # Convert to float
        self.assertTrue(df['total_supply'].dtype == 'float64')

        # Check if the data matches the mock response for a specific timestamp
        timestamp = pd.to_datetime(1702252800000, unit='ms')
        expected_supply = float(mock_response.json()['total_supply'][0][1])
        self.assertAlmostEqual(df.at[timestamp, 'total_supply'], expected_supply, places=2)

    # ---------- token_lists/{asset_platform_id}/all ---------- #
    @patch('requests.Session.get')
    def test_all_tokens_list(self, mock_get):
        """Test fetching a full list of tokens for a specific blockchain network."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.token_lists_platform_id_all_response
        mock_get.return_value = mock_response

        # Call the method
        asset_platform_id = 'ethereum'  # Replace with actual platform ID for a real test
        df = self.api.all_tokens_list(asset_platform_id)

        # Ensure the returned object is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Test the structure of the DataFrame
        expected_columns = ['chainId', 'address', 'name', 'symbol', 'decimals', 'logoURI']
        self.assertListEqual(list(df.columns), expected_columns)

        # Test the data types of the DataFrame columns
        for col in expected_columns:
            self.assertIn(df[col].dtype, ['int64', 'object'])

        # Check if the data matches the mock response for a specific token
        expected_token = mock.token_lists_platform_id_all_response['tokens'][0]
        for col in expected_columns:
            self.assertEqual(df.iloc[0][col], expected_token[col])


if __name__ == '__main__':
    unittest.main()
