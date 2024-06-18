import unittest
from unittest.mock import patch, MagicMock

from asset_platforms import AssetPlatforms
import mock_responses as mock


class TestAssetPlatforms(unittest.TestCase):

    def setUp(self):
        """Initialize the AssetPlatforms API for testing."""
        self.cg = AssetPlatforms(
            api_key='test_api_key',
            pro_api=False,
            retries=5
        )

    @patch('pycgapi.base.requests.Session.get')
    def test_asset_platforms_list(self, mock_get):
        """Test fetching all asset platforms without any filter."""
        # Prepare the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = mock.asset_platforms_response
        mock_get.return_value = mock_response

        # Execute the function
        asset_platforms_df = self.cg.asset_platforms_list()

        # Expected columns from the response
        expected_columns = ['id', 'chain_identifier', 'name', 'shortname',
                            'native_coin_id']

        # Check if DataFrame has the expected columns
        self.assertListEqual(list(asset_platforms_df.columns), expected_columns)

        # Verify the DataFrame contains correct data
        for i, row in enumerate(mock.asset_platforms_response):
            for col in expected_columns:
                self.assertEqual(asset_platforms_df.iloc[i][col], row[col])

    @patch('pycgapi.base.requests.Session.get')
    def test_asset_platforms_list_with_platform_filter(self, mock_get):
        """Test fetching asset platforms with 'nft' filter."""
        # Prepare a different mock response for when the NFT filter is applied
        mock_response = MagicMock()
        mock_response.json.return_value = mock.filtered_asset_platforms_response
        mock_get.return_value = mock_response

        # Execute the function with the 'nft' filter
        asset_platforms_df = self.cg.asset_platforms_list(
            platform_filter="nft")

        # Expected columns remain the same
        expected_columns = ['id', 'chain_identifier', 'name', 'shortname',
                            'native_coin_id']

        # Check if DataFrame has the expected columns
        self.assertListEqual(list(asset_platforms_df.columns), expected_columns)


if __name__ == '__main__':
    unittest.main()
