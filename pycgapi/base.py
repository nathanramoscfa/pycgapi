import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .module_mapping import module_to_class


class CoinGeckoAPI:
    """
    A Python wrapper for the CoinGecko API which allows for easy
    retrieval of financial and metadata on cryptocurrencies from the
    CoinGecko API.

    Attributes:
        API_BASE_URL (str): Default base URL for accessing the public
            CoinGecko API.
        PRO_API_BASE_URL (str): Base URL for accessing the Pro
            CoinGecko API which offers higher rate limits and more
            comprehensive data.
        session (requests.Session): Shared HTTP session for all API
            requests.

    """
    API_BASE_URL = 'https://api.coingecko.com/api/v3/'
    PRO_API_BASE_URL = 'https://pro-api.coingecko.com/api/v3/'
    session = None

    def __init__(
        self,
        api_key: str = None,
        pro_api: bool = False,
        retries: int = 5
    ):
        """
        Initializes the CoinGeckoAPI class, setting up the API key,
        deciding whether to use the Pro API, and configuring the number
        of retries for requests.

        The Pro API provides higher rate limits and more comprehensive
        data, which requires an API key.

        Args:
            api_key (str, optional): The API key needed for accessing
                the Pro API. Defaults to None, for public API access.
            pro_api (bool, optional): Flag to determine whether to use
                the Pro API features. Defaults to False.
            retries (int, optional): The number of retries for each
                request, useful for handling potential transient network
                issues. Defaults to 5.

        """
        self.api_key = api_key
        self.pro_api = pro_api
        self.base_url = self.PRO_API_BASE_URL if pro_api else self.API_BASE_URL
        if CoinGeckoAPI.session is None:
            CoinGeckoAPI.session = self._create_session(retries)
        self.modules = {}

    @staticmethod
    def _create_session(retries: int):
        """
        Creates a requests session with retry logic.

        Args:
            retries (int): Number of retries for the session.

        Returns:
            requests.Session: A configured requests session with retry
                capabilities.

        """
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        return session

    def __getattr__(self, name):
        """
        Retrieves the specified module from the API configuration.

        Args:
            name (str): The name of the module to retrieve.

        Returns:
            object: The module object from the API configuration.

        Raises:
            AttributeError: If the module name is not found in the
                module mapping.

        """
        if name not in self.modules:
            try:
                class_name, module_path = module_to_class[name]
                module = __import__(
                    f'pycgapi.{module_path}',
                    fromlist=[class_name]
                )
                self.modules[name] = getattr(module, class_name)(
                    self.api_key, self.pro_api)
            except KeyError:
                raise AttributeError(f"Module {name} not found in "
                                     f"API configuration.")
            except ImportError as e:
                print(f"Failed to import {name}: {e}")
                raise
        return self.modules[name]

    def _request(self, endpoint: str, params: dict = None):
        """
        Sends a request to an API endpoint and handles HTTP errors.

        Args:
            endpoint (str): The API endpoint for the request.
            params (dict, optional): Parameters to include in the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            Exception: Exceptions based on HTTP status or other errors
                during the request process.

        """
        url = self.build_endpoint(endpoint)
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
            if self.api_key and self.pro_api else ''
        }
        response = CoinGeckoAPI.session.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, **params):
        """
        Convenience method to send a GET request to the specified
        endpoint.

        Args:
            endpoint (str): The API endpoint to make a GET request to.
            **params: Arbitrary keyword arguments passed along to the
                GET request.

        Returns:
            dict: The JSON response from the GET request.

        """
        return self._request(endpoint, params=params)

    def build_endpoint(self, endpoint: str) -> str:
        """
        Constructs the complete endpoint URL.

        Args:
            endpoint (str): The specific API endpoint.

        Returns:
            str: The complete URL to be used for the API call.

        """
        if self.pro_api:
            separator = '&' if '?' in endpoint else '?'
            endpoint = f"{endpoint}{separator}x_cg_pro_api_key={self.api_key}"
        return f'{self.base_url}{endpoint}'

    @classmethod
    def end_session(cls):
        """
        Closes the shared HTTP session among all instances and ensures
        clean shutdown of resources, resetting the session attribute
        to None.
        """
        if cls.session:
            cls.session.close()
            cls.session = None
            return "Session closed successfully."
        return "Session was already closed."
