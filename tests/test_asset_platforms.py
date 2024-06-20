import unittest
from unittest.mock import patch
import pandas as pd

from ..pycgapi import CoinGeckoAPI


class TestAssetPlatforms(unittest.TestCase):

    @patch.object(CoinGeckoAPI, '_get')
    def test_asset_platforms_list(self, mock_get):
        # Mock response data
        mock_response = [
            {'id': 'ethereum', 'chain_identifier': 1, 'name': 'Ethereum'},
            {'id': 'binance-smart-chain', 'chain_identifier': 56,
             'name': 'Binance Smart Chain'}
        ]
        mock_get.return_value = mock_response

        # Initialize the CoinGeckoAPI class
        cg = CoinGeckoAPI(api_key='test_key', pro_api=True)

        # Test without filter
        result = cg.asset_platforms.asset_platforms_list()
        mock_get.assert_called_once_with('asset_platforms')
        expected_df = pd.DataFrame(mock_response)
        pd.testing.assert_frame_equal(result, expected_df)

        # Reset mock
        mock_get.reset_mock()

        # Test with filter
        result = cg.asset_platforms.asset_platforms_list(platform_filter='nft')
        mock_get.assert_called_once_with('asset_platforms', filter='nft')
        pd.testing.assert_frame_equal(result, expected_df)

    @patch.object(CoinGeckoAPI, '_get')
    def test_all_tokens_list(self, mock_get):
        # Mock response data
        mock_response = {
            'tokens': [
                {'name': 'Wrapped Ether', 'symbol': 'WETH', 'address': '0x...'},
                {'name': 'USD Coin', 'symbol': 'USDC', 'address': '0x...'}
            ]
        }
        mock_get.return_value = mock_response

        # Initialize the CoinGeckoAPI class
        cg = CoinGeckoAPI(api_key='test_key', pro_api=True)

        # Test all_tokens_list
        result = cg.asset_platforms.all_tokens_list(
            asset_platform_id='ethereum')
        mock_get.assert_called_once_with('token_lists/ethereum/all.json')
        expected_df = pd.DataFrame(mock_response['tokens'])
        pd.testing.assert_frame_equal(result, expected_df)


if __name__ == '__main__':
    unittest.main()
