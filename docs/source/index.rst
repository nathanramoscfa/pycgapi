.. CoinGeckoAPI documentation master file, created by
   sphinx-quickstart on Sat Jan  6 18:30:58 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ../../media/logo.png
   :alt: Logo
   :align: center
   :scale: 60%

.. image:: https://img.shields.io/badge/License-MIT-brightgreen.svg
   :target: https://img.shields.io/badge/
   :alt: License

.. image:: https://github.com/nathanramoscfa/coingeckoapi/actions/workflows/main.yml/badge.svg
   :target: https://github.com/nathanramoscfa/coingeckoapi/actions/workflows/main.yml
   :alt: pytest

.. image:: https://codecov.io/gh/nathanramoscfa/coingeckoapi/graph/badge.svg?token=I1CRHDN73S
   :target: https://codecov.io/gh/nathanramoscfa/coingeckoapi


Table of Contents
=================

.. contents::
    :depth: 2


Overview
========
``coingeckoapi`` is an unofficial Python wrapper for the CoinGecko API (V3). It's designed to process API endpoint
responses to easy-to-use ``pandas`` DataFrames. From simple price checks to complex historical
data analysis, ``coingeckoapi`` facilitates seamless integration with the CoinGecko API. For more information on the
official CoinGecko API, please refer to their `documentation <https://www.coingecko.com/api/documentation>`_.


Features
========
``coingeckoapi`` provides a user-friendly and efficient way to interact with
the CoinGecko API. It simplifies the process of retrieving cryptocurrency data, offering the following features:

#. **Simplified Endpoints**: Access to CoinGecko's extensive cryptocurrency data through easy-to-use Python methods.
#. **Comprehensive Data Access**: Fetch latest prices, market caps, trading volumes, historical data, and more for over
   thousands of cryptocurrencies.
#. **Enhanced Functionality for Pro Users**: Special endpoints for Pro API users, including faster data updates and
   access to exclusive data sets.
#. **Multi-Category Support**: Access to various categories, including coins, exchanges, derivatives,
   decentralized finance (DeFi), and non-fungible tokens (NFTs).
#. **Historical Data Retrieval**: Obtain historical market data with customizable granularity, providing valuable
   insights into cryptocurrency trends and movements.
#. **Global Cryptocurrency Statistics**: Overview of global cryptocurrency statistics, including market caps, trading
   volumes, and dominance percentages.
#. **Rate Limit Management**: Handles API rate limits efficiently, ensuring seamless data retrieval without hitting
   rate limits.
#. **Error Handling and Reporting**: Comprehensive error handling to report and manage API request issues effectively.
#. **Real-time Data Updates**: Offers real-time updates on cryptocurrency prices and market changes, crucial for timely
   analysis and decision-making.
#. **Easy Integration**: Designed for easy integration into financial analysis tools, trading bots, and cryptocurrency
   applications.

``coingeckoapi`` is ideal for cryptocurrency enthusiasts, financial analysts, data scientists, and developers seeking a
robust and comprehensive solution for accessing CoinGecko's extensive cryptocurrency data.


Installation
============
``coingeckoapi`` is available on `PyPI <https://pypi.org/project/coingeckoapi/>`_ and can be installed using
``pip``:

.. code-block:: bash

    pip install coingeckoapi

Alternatively, you can install the latest version of ``coingeckoapi`` directly from the
`GitHub <https://www.coingecko.com/api/documentation>`_ repository.

.. code-block:: bash

    pip install git+https://github.com/nathanramoscfa/coingeckoapi.git


API Key
=======

You do not need an API key to use the Public API. You will need an API key to use the Pro API. To obtain an API key,
please visit the `CoinGecko API <https://www.coingecko.com/api>`_ page and follow the instructions. This package comes
bundled with `keyring <https://github.com/jaraco/keyring>`_ to save and retrieve your API key securely
without having to hardcode it. To save your API key, simply run the following code in a Python console or Jupyter
Notebook:

.. code-block:: python

    import keyring

    # replace MY_API_KEY with your API key
    keyring.set_password('coingecko', 'api_key', 'MY_API_KEY')
    print(keyring.get_password('coingecko', 'api_key'))

Output:

::

    'MY_API_KEY'

CoinGecko offers various `API plans <https://www.coingecko.com/en/api/pricing>`_ tailored to different user needs. Below
is a summary table of the key features of each plan:

+-------------+----------------+------------------------+----------------+-----------------------+
| Plan        | Monthly Price  | Annual Price (Monthly) | Rate Limit/Min | Call Credits (Monthly)|
+=============+================+========================+================+=======================+
| Demo (Beta) | Free           | Free                   | 10-30          | 10K                   |
+-------------+----------------+------------------------+----------------+-----------------------+
| Analyst     | $129           | $103                   | 500            | 500K                  |
+-------------+----------------+------------------------+----------------+-----------------------+
| Lite        | $499           | $399                   | 500            | 2M                    |
+-------------+----------------+------------------------+----------------+-----------------------+
| Pro         | $999           | $799                   | 1000           | 5M                    |
+-------------+----------------+------------------------+----------------+-----------------------+
| Enterprise  | Custom Pricing | Custom Pricing         | Custom         | Custom                |
+-------------+----------------+------------------------+----------------+-----------------------+


Quick Start
===========

To initialize the ``coingeckoapi`` client, simply run the following code based on your API plan:

**Demo (Beta) API:**

.. code-block:: python

    from coingeckoapi import CoinGeckoAPI
    api = CoinGeckoAPI()  # no API key required for public API

**Paid Plan API:**

.. code-block:: python

    import keyring
    from coingeckoapi import CoinGeckoAPI

    # gets your API key from keyring
    api_key = keyring.get_password(
       'coingecko',
       'api_key'
    )

    # must provide api_key and set pro_api=True
    api = CoinGeckoAPI(api_key, pro_api=True)

**Ping the CoinGecko API server:**

.. code-block:: python

    api.status_check()

Output:

::

    API Server Status: {'gecko_says': '(V3) To the Moon!'}

The output above confirms a successful connection to the CoinGecko API server.

Usage Examples
==============

See the `examples <https://github.com/nathanramoscfa/coingeckoapi/examples>`_ directory for detailed examples of all
endpoints. Here are a few examples of ``coingeckoapi``:

**Get a list of all supported coins:**

.. code-block:: python

    coins = api.coins_list()
    coins.head()

Output:

::

                        symbol                 name
    id
    01coin                 zoc               01coin
    0chain                 zcn                  Zus
    0-knowledge-network    0kn  0 Knowledge Network
    0-mee                  ome                O-MEE
    0vix-protocol          vix        0VIX Protocol

**Get a list of all supported coins with price, volume, and market-related data:**

.. code-block:: python

    coin_markets_data = api.coins_market_data()
    show_columns = [
        'symbol', 'name', 'current_price', 'market_cap', 'total_volume'
    ]
    print('Available Fields: {}'.format(sorted(coin_markets_data.columns)))
    print(coin_markets_data[show_columns].head())

Output:

::

   Available Fields: ['ath', 'ath_change_percentage', 'ath_date', 'atl',
   'atl_change_percentage', 'atl_date', 'circulating_supply', 'current_price',
   'fully_diluted_valuation', 'high_24h', 'image', 'last_updated', 'low_24h',
   'market_cap', 'market_cap_change_24h', 'market_cap_change_percentage_24h',
   'market_cap_rank', 'max_supply', 'name', 'price_change_24h',
   'price_change_percentage_24h', 'roi', 'symbol', 'total_supply',
   'total_volume']

                symbol      name  current_price    market_cap  total_volume
    id
    bitcoin        btc   Bitcoin      43410.000  850590460912   29791306848
    ethereum       eth  Ethereum       2223.840  267274033503   18135533011
    tether        usdt    Tether          1.002   92977544355   51440182305
    binancecoin    bnb       BNB        311.890   48011725773    1578466144
    solana         sol    Solana         96.810   41708642386    3237650635

**Get a list of supported fiat-currencies:**

.. code-block:: python

    supported_vs_currencies = api.supported_currencies()
    print('Available Vs. Currencies: {}'.format(
        sorted(supported_vs_currencies)))

Output:

::

    Available Vs. Currencies: ['aed', 'ars', 'aud', 'bch', 'bdt', 'bhd',
    'bits', 'bmd', 'bnb', 'brl', 'btc', 'cad', 'chf', 'clp', 'cny', 'czk',
    'dkk', 'dot', 'eos', 'eth', 'eur', 'gbp', 'gel', 'hkd', 'huf', 'idr',
    'ils', 'inr', 'jpy', 'krw', 'kwd', 'link', 'lkr', 'ltc', 'mmk', 'mxn',
    'myr', 'ngn', 'nok', 'nzd', 'php', 'pkr', 'pln', 'rub', 'sar', 'sats',
    'sek', 'sgd', 'thb', 'try', 'twd', 'uah', 'usd', 'vef', 'vnd', 'xag',
    'xau', 'xdr', 'xlm', 'xrp', 'yfi', 'zar']

**Get the current price of a list of cryptocurrencies:**

.. code-block:: python

    coin_ids = ['bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana']
    price = api.get_simple_prices(coin_ids)
    price

Output:

::

                         usd
    binancecoin    320.25000
    bitcoin      43201.00000
    ethereum      2239.91000
    solana         101.26000
    tether           0.99994

**Get the historical market data for a list of cryptocurrencies:**

.. code-block:: python

    coin_ids = ['bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana']
    coins_historical_data = api.multiple_coins_historical_data(coin_ids)
    print('Available Keys: {}'.format(sorted(coins_historical_data.keys())))
    coins_historical_data['price'].head()

Output:

::

      100%|██████████| 5/5 [00:02<00:00,  1.75it/s]
      Available Keys: ['market_cap', 'price', 'total_volume']


                                     bitcoin    ethereum    tether  binancecoin  \
      timestamp
      2020-04-11 00:00:00+00:00  6864.694257  157.740158  1.001752    13.718826
      2020-04-12 00:00:00+00:00  6878.781213  158.327878  1.001414    13.826759
      2020-04-13 00:00:00+00:00  6913.158787  158.863826  0.996086    14.265117
      2020-04-14 00:00:00+00:00  6857.538538  156.701359  0.998972    15.045573
      2020-04-15 00:00:00+00:00  6860.178536  158.267151  1.000622    15.582721

                                   solana
      timestamp
      2020-04-11 00:00:00+00:00  0.957606
      2020-04-12 00:00:00+00:00  0.784711
      2020-04-13 00:00:00+00:00  0.875994
      2020-04-14 00:00:00+00:00  0.786712
      2020-04-15 00:00:00+00:00  0.666673


Testing
=======

To run the test suite with coverage analysis, navigate to the root directory of the project and use the following command:

.. code-block:: bash

   coverage run -m unittest discover -s tests

This command uses coverage to run all tests in the tests directory and collect coverage data as specified in the
.coveragerc file. After running the tests, you can generate a report to see the coverage percentage with:

.. code-block:: bash

   coverage report

Or, to generate an HTML report showing line-by-line coverage:

.. code-block:: bash

   coverage html

This will create a new directory named ``htmlcov``. Open the ``index.html`` file in this directory with a web browser
to view the detailed coverage report.

Roadmap
=======

- Add asynchronous functionality to improve performance.

Contributing
============

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

License
=======

``coingeckoapi`` is released under the MIT License. See
`LICENSE <https://github.com/nathanramoscfa/coingeckoapi/LICENSE>`_ file for more details.

Contact
=======
Find me on `LinkedIn <https://www.linkedin.com/in/nathanramos/>`_
or schedule a meeting on `Calendly <https://calendly.com/nrcapitalmanagement/coingeckoapi-meeting>`_.

API Contents
============

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   coingeckoapi

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
