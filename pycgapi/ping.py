from .base import CoinGeckoAPI


class Ping(CoinGeckoAPI):
    def ping(self):
        """
        Checks the CoinGecko API server status to ensure connectivity and
        responsiveness. Useful for verifying API availability and network issues.

        Returns:
            dict: A response from the API that includes a message confirming
                the connection, typically a "gecko_says" response.

        Notes:
            - Endpoint: 'ping'.
            - This is a simple API call with no parameters, returning a basic
              message from the server.
            - Useful for initial setup tests and periodic connectivity checks.
            - CoinGecko API Documentation:
              https://docs.coingecko.com/reference/ping-server
            - For additional status updates and maintenance info, visit:
              https://status.coingecko.com

        """
        endpoint = 'ping'
        return self._get(endpoint)
