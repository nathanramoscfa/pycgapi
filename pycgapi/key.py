import pandas as pd

from .base import CoinGeckoAPI


class APIKeyData(CoinGeckoAPI):
    def fetch_api_usage(self) -> pd.DataFrame:
        """
        Retrieves API usage statistics from the CoinGecko PRO API, including
        details about the current plan and API call credits.

        Returns:
            pd.DataFrame: A DataFrame presenting API usage details in a
                structured format. Columns include Plan, Rate Limit per
                Minute, Monthly Call Credit, Total Monthly Calls, and
                Remaining Monthly Calls.

        Notes:
            - Endpoint: 'key'
            - The API response includes detailed usage statistics such as rate
              limits and call counts.
            - For a comprehensive overview, visit the API usage dashboard:
              https://www.coingecko.com/en/developers/dashboard
            - API Documentation:
              https://docs.coingecko.com/reference/api-usage

        """
        endpoint = 'key'
        response = self._get(endpoint)
        data = {
            'Plan': [response['plan']],
            'Rate Limit per Minute': [
                response['rate_limit_request_per_minute']],
            'Monthly Call Credit': [response['monthly_call_credit']],
            'Total Monthly Calls': [response['current_total_monthly_calls']],
            'Remaining Monthly Calls': [
                response['current_remaining_monthly_calls']]
        }
        df = pd.DataFrame(data)
        df_transposed = df.transpose()
        df_transposed.columns = ['API Usage']
        df_transposed['API Usage'] = df_transposed['API Usage'].apply(
            lambda x: "{:,}".format(x) if isinstance(x, int) else x
        )
        return df_transposed
