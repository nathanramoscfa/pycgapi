import sys
import os

# Set the path so that the script can import cgapi properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cgapi import CoinGeckoAPI


def initialize_api():
    """
    Initialize the CoinGeckoAPI client.
    """

    # For Demo (Beta) API (Public API, no API key required)
    api = CoinGeckoAPI()

    return api


def main():
    api = initialize_api()

    # Ping the CoinGecko API server
    status = api.status_check()
    print("API Server Status:", status)


if __name__ == "__main__":
    main()
