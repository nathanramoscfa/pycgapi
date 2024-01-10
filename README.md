<style>
  .center {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 40%;
  }
</style>

<p>
  <img src="media/logo.png" alt="Logo" class="center">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![pytest](https://github.com/nathanramoscfa/pycgapi/actions/workflows/tests.yml/badge.svg)](https://github.com/nathanramoscfa/pycgapi/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/nathanramoscfa/pycgapi/graph/badge.svg?token=I1CRHDN73S)](https://codecov.io/gh/nathanramoscfa/pycgapi)
[![Documentation Status](https://readthedocs.org/projects/coingeckoapi/badge/?version=latest)](https://coingeckoapi.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/pycgapi)
![Python Version](https://img.shields.io/pypi/pyversions/pycgapi)

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [API Key](#api-key)
5. [Quick Start](#quick-start)
6. [Usage Examples](#usage-examples)
7. [Available Methods](#available-methods)
   - [ping](#ping)
   - [simple](#simple)
   - [coins](#coins)
   - [contract](#contract)
   - [asset_platforms](#asset_platforms)
   - [categories](#categories)
   - [exchanges](#exchanges)
   - [derivatives](#derivatives)
   - [nfts (beta)](#nfts-beta)
   - [exchange_rates](#exchange_rates)
   - [search](#search)
   - [trending](#trending)
   - [global](#global)
   - [companies (beta)](#companies-beta)
   - [paid plan (exclusive)](#paid-plan-exclusive)
   - [enterprise plan (exclusive)](#enterprise-plan-exclusive)
8. [Running on Docker](#running-on-docker)
9. [Testing](#testing)
10. [Roadmap](#roadmap)
11. [Contributing](#contributing)
12. [Change Log](#change-log)
13. [License](#license)
14. [Contact](#contact)


## Overview
`pycgapi` is an unofficial Python wrapper for the CoinGecko API (V3). It's designed to process API endpoint
responses to easy-to-use `pandas` DataFrames.  From simple price checks to complex historical data analysis, 
`pycgapi` facilitates seamless integration with the CoinGecko API. For more information on the 
official CoinGecko API, please refer to the official [documentation](https://www.coingecko.com/api/documentation).

## Features

`pycgapi` provides a user-friendly and efficient way to interact with 
the CoinGecko API. It simplifies the process of retrieving cryptocurrency data, offering the following features:

1. **Simplified Endpoints**: Access to CoinGecko's extensive cryptocurrency data through easy-to-use Python methods.
2. **Comprehensive Data Access**: Fetch latest prices, market caps, trading volumes, historical data, and more for over 
   thousands of cryptocurrencies.
3. **Enhanced Functionality for Pro Users**: Special endpoints for Pro API users, including faster data updates and 
   access to exclusive data sets.
4. **Multi-Category Support**: Access to various categories, including coins, exchanges, derivatives, 
   decentralized finance (DeFi), and non-fungible tokens (NFTs).
5. **Historical Data Retrieval**: Obtain historical market data with customizable granularity, providing valuable 
   insights into cryptocurrency trends and movements.
6. **Global Cryptocurrency Statistics**: Overview of global cryptocurrency statistics, including market caps, trading 
   volumes, and dominance percentages.
7. **Rate Limit Management**: Handles API rate limits efficiently, ensuring seamless data retrieval without hitting 
   rate limits.
8. **Error Handling and Reporting**: Comprehensive error handling to report and manage API request issues effectively.
9. **Real-time Data Updates**: Offers real-time updates on cryptocurrency prices and market changes, crucial for timely 
   analysis and decision-making.
10. **Easy Integration**: Designed for easy integration into financial analysis tools, trading bots, and cryptocurrency 
    applications.

`pycgapi` is ideal for cryptocurrency enthusiasts, financial analysts, data scientists, and developers seeking a 
robust and comprehensive solution for accessing CoinGecko's extensive cryptocurrency data.

## Installation
To install `pycgapi`, simply run:

```bash
pip install pycgapi
```

Or, clone from GitHub and install:

```bash
git clone https://github.com/nathanramoscfa/pycgapi.git
cd pycgapi
python setup.py install
```

## API Key
You do not need an API key to use the Public API. You will need an API key to use the Pro API. To obtain an API key,
please visit the [CoinGecko API](https://www.coingecko.com/api) page and follow the instructions. This package comes 
bundled with [keyring](https://github.com/jaraco/keyring) to save and retrieve your API key securely 
without having to hardcode it. To save your API key, simply run the following code in a Python console or Jupyter 
Notebook:

```python
import keyring
keyring.set_password('coingecko', 'api_key', 'MY_API_KEY')  # replace MY_API_KEY with your API key
print(keyring.get_password('coingecko', 'api_key'))
```
Output:
```
'MY_API_KEY'
```

### CoinGecko API Plans and Rate Limits

CoinGecko offers various [API plans](https://www.coingecko.com/en/api/pricing) tailored to different user needs. Below 
is a summary table of the key features of each plan:

| Plan        | Monthly Price  | Annual Price (Monthly) | Rate Limit/Min | Call Credits (Monthly |
|-------------|----------------|------------------------|----------------|-----------------------|
| Demo (Beta) | Free           | Free                   | 10-30          | 10K                   |
| Analyst     | $129           | $103                   | 500            | 500K                  |
| Lite        | $499           | $399                   | 500            | 2M                    |
| Pro         | $999           | $799                   | 1000           | 5M                    |
| Enterprise  | Custom Pricing | Custom Pricing         | Custom         | Custom                |

## Quick Start
To initialize the `pycgapi` client, simply run the following code based on your API plan:

**Demo (Beta) API:**

```python
from pycgapi import CoinGeckoAPI
api = CoinGeckoAPI()  # no API key required for public API
```

**Paid Plan API:**

```python
import keyring
from pycgapi import CoinGeckoAPI
api_key = keyring.get_password('coingecko', 'api_key')  # gets your API key
api = CoinGeckoAPI(api_key, pro_api=True)  # must provide api_key and set pro_api=True
```
**Ping the CoinGecko API server:**

```python
api.status_check()
```

Output:
```
API Server Status: {'gecko_says': '(V3) To the Moon!'}
```

The output above confirms a successful connection to the CoinGecko API server. 

## Usage Examples
For detailed examples of all endpoints, see the 
[examples directory](https://github.com/nathanramoscfa/pycgapi/tree/main/examples). Here are a few examples of `pycgapi`:

**Get a list of all supported coins:**

```python
coins = api.coins_list()
coins.head()
```
Output:
```
                    symbol                 name
id                                             
01coin                 zoc               01coin
0chain                 zcn                  Zus
0-knowledge-network    0kn  0 Knowledge Network
0-mee                  ome                O-MEE
0vix-protocol          vix        0VIX Protocol
```

**Get a list of all supported coins with price, volume, and market-related data:**

```python
coins = api.coins_market_data()[['symbol', 'name', 'current_price', 'market_cap', 'total_volume']]
print(coins.head())
```
Output:
```
            symbol      name  current_price    market_cap  total_volume
id                                                                     
bitcoin        btc   Bitcoin      43410.000  850590460912   29791306848
ethereum       eth  Ethereum       2223.840  267274033503   18135533011
tether        usdt    Tether          1.002   92977544355   51440182305
binancecoin    bnb       BNB        311.890   48011725773    1578466144
solana         sol    Solana         96.810   41708642386    3237650635
```

**Get a list of supported fiat-currencies:**

```python
supported_vs_currencies = api.supported_currencies()
print('Available Vs. Currencies: {}'.format(sorted(supported_vs_currencies)))
```
Output:
```
Available Vs. Currencies: ['aed', 'ars', 'aud', 'bch', 'bdt', 'bhd', 'bits', 'bmd', 'bnb', 'brl', 'btc', 'cad', 'chf', 
'clp', 'cny', 'czk', 'dkk', 'dot', 'eos', 'eth', 'eur', 'gbp', 'gel', 'hkd', 'huf', 'idr', 'ils', 'inr', 'jpy', 'krw', 
'kwd', 'link', 'lkr', 'ltc', 'mmk', 'mxn', 'myr', 'ngn', 'nok', 'nzd', 'php', 'pkr', 'pln', 'rub', 'sar', 'sats', 'sek', 
'sgd', 'thb', 'try', 'twd', 'uah', 'usd', 'vef', 'vnd', 'xag', 'xau', 'xdr', 'xlm', 'xrp', 'yfi', 'zar']
```

**Get the current price of a list of cryptocurrencies:**

```python
coin_ids = ['bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana']
price = api.get_simple_prices(coin_ids)
price
```
Output:
```
                     usd
binancecoin    320.25000
bitcoin      43201.00000
ethereum      2239.91000
solana         101.26000
tether           0.99994
```

**Get the historical market data for a list of cryptocurrencies:**

```python
coin_ids = ['bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana']
coins_historical_data = api.multiple_coins_historical_data(coin_ids)
print('Available Keys: {}'.format(sorted(coins_historical_data.keys())))
coins_historical_data['price'].head()
```
Output:
```
100%|██████████| 5/5 [00:01<00:00,  2.68it/s]
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
```

## Available Methods
`pycgapi` offers a wide range of methods for accessing cryptocurrency data. For a complete list of available
methods, please refer to the [documentation](https://nathanramoscfa.github.io/pycgapi/). 

<details><summary>ping</summary>
<p>

* **/ping** - Check API server status.

```python
api.status_check()
```
</details>

<details><summary>simple</summary>
<p>

* **/simple/price** - Get the current price of any cryptocurrencies in any other supported currencies that you need.
```python
api.simple_prices(coin_ids)
```

* **/simple/supported_vs_currencies** - Get list of supported_vs_currencies.

```python
api.supported_currencies()
```
</details>

<details><summary>coins</summary>
<p>

* **/coins/list** - List all supported coins id, name and symbol (no pagination required).

```python
api.coins_list()
```

* **/coins/markets** - List all supported coins price, market cap, volume, and market related data.

```python
api.coins_market_data()
api.top_coins_market_data(top_n=10)
```

* **/coins/{id}** - Get current data (name, price, market, ... including exchange tickers) for a coin.

```python
api.coin_info(coin_id='bitoin')
```

* **/coins/{id}/tickers** - Get coin tickers (paginated to 100 items).

```python
api.coin_market_tickers(coin_id='bitoin')
```

* **/coins/{id}/history** - Get historical data (name, price, market, stats) at a given date for a coin.
```python
api.coin_historical_on_date(coin_id='bitoin', date='12-31-2023')
```

* **/coins/{id}/market_chart** - Get historical market data include price, market cap, and 24h volume (granularity auto).

```python
api.coin_historical_market_data(coin_id='bitoin')
api.multiple_coins_historical_data(coin_ids=['bitoin', 'ethereum', 'tether', 'binancecoin', 'solana'])
```

* **/coins/{id}/market_chart/range** - Get historical market data include price, market cap, and 24h volume within a 
  range of timestamp (granularity auto).

```python
api.coin_historical_market_data(coin_id='bitoin', from_date='12-31-2022', to_date='12-31-2023')
api.multiple_coins_historical_data(coin_ids=['bitoin', 'ethereum', 'tether'], from_date='12-31-2022',
                                   to_date='12-31-2023')
```

* **/coins/{id}/ohlc** - Get coin's OHLC (candlestick) data.

```python
api.coin_ohlc_data(coin_id='bitoin')
api.multiple_coins_ohlc_data(coin_ids=['bitoin', 'ethereum', 'tether', 'binancecoin', 'solana'])
```
</details>

<details><summary>contract</summary>
<p>

* **/coins/{id}/contract/{contract_address}** - Get coin info from contract address.

```python
api.coin_by_contract(platform_id='ethereum', contract_address='0x5a98fcbea516cf06857215779fd812ca3bef1b32')
```

* **/coins/{id}/contract/{contract_address}/market_chart** - Get historical market data include price, market cap, and 
  24h volume (granularity auto).

```python
api.contract_historical_market_data(platform_id='ethereum',
                                    contract_address='0x5a98fcbea516cf06857215779fd812ca3bef1b32')
```

* **/coins/{id}/contract/{contract_address}/market_chart/range** - Get historical market data include price, market cap, 
  and 24h volume within a range of timestamp (granularity auto).

```python
api.contract_historical_market_data(platform_id='ethereum',
                                    contract_address='0x5a98fcbea516cf06857215779fd812ca3bef1b32',
                                    from_date='12-31-2022', to_date='12-31-2023')
```
</details>

<details><summary>asset_platforms</summary>
<p>

* **/asset_platforms** - List all asset platforms (Blockchain networks).

```python
api.asset_platforms_list()
```
</details>

<details><summary>categories</summary>
<p>

* **/coins/categories/list** - List all categories.

```python
api.cryptocurrency_categories_list()
```

* **/coins/categories** - List all categories with market data.

```python
api.categories_market_data()
```
</details>

<details><summary>exchanges</summary>
<p>

* **/exchanges** - List all exchanges.

```python
api.active_exchanges_list()
```

* **/exchanges/list** - List all exchanges name and identifier.

```python
api.all_exchanges_list()
```

* **/exchanges/{id}** - Get exchange volume in BTC and top 100 tickers for a specific exchange.

```python
api.exchange_volume_data(exchange_id='binance')
```

* **/exchanges/{id}/tickers** - Get paginated tickers for a specific exchange (paginated, 100 tickers per page).

```python
api.exchange_market_tickers(exchange_id='binance')
```

* **/exchanges/{id}/volume_chart** - Get volume_chart data for a specific exchange.

```python
api.exchange_historical_volume(exchange_id='binance')
```

* **/exchanges/{id}/volume_chart/range** - Get volume_chart data for a specific exchange within a range of timestamp.

```python
api.exchange_historical_volume(exchange_id='binance', from_date='12-31-2022', to_date='12-31-2023')
```
</details>

<details><summary>derivatives</summary>
<p>

* **/derivatives** - List all derivative tickers.

```python
api.derivatives_market_tickers()
```

* **/derivatives/exchanges** - List all derivative exchanges.

```python
api.derivatives_exchanges_list()
```

* **/derivatives/exchanges/{id}** - Get detailed data for a specific derivatives exchange.

```python
api.derivatives_exchange_info(exchange_id='binance_futures')
```

* **/derivatives/exchanges/list** - List all derivatives exchanges name and identifiers.
```python
api.all_derivatives_exchanges_list()
```
</details>

<details><summary>nfts (beta)</summary>
<p>

* **/nfts/list** - Get list of all supported NFT ids. 
```python
api.nfts_supported()
```

* **/nfts/{id}** - Get current data for a specific NFT collection.

```python
api.nft_collection_info(nft_id='bored-ape-yacht-club')
api.nft_collections_info(nft_ids=['cryptopunks', 'bored-ape-yacht-club'])
```

* **nfts/{asset_platform_id}/contract/{contract_address}** - Get current data for a specific NFT contract address.

```python
api.nft_collection_info(asset_platform_id='ethereum', contract_address='0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d')
```
</details>

<details><summary>exchange_rates</summary>
<p>

* **/exchange_rates** - Get BTC-to-Currency exchange rates.

```python
api.btc_exchange_rates()
```
</details>

<details><summary>search</summary>
<p>

* **/search** - Search for coins, categories, and markets listed on CoinGecko.
```python
api.search_coingecko(query='bitcoin')
```
</details>

<details><summary>trending</summary>
<p>

* **/search/trending** - Get trending search coins (Top-7) on CoinGecko in the last 24 hours.

```python
api.trending_searches()
```
</details>

<details><summary>global</summary>
<p>

* **/global** - Get cryptocurrency global data.

```python
api.global_crypto_stats()
```

* **/global/decentralized_finance_defi** - Get cryptocurrency global decentralized finance(defi) data.

```python
api.global_defi_stats()
```
</details>

<details><summary>companies (beta)</summary>
<p>

* **/companies/public_treasury/{coin_id}** - Get public companies that hold this coin as part of their treasury.

```python
api.companies_holdings(coin_id='bitcoin')
```
</details>

<details><summary>paid plan (exclusive)</summary>
<p>

* **/coins/list/new** - Get the latest 200 coins recented listed on CoinGecko.

```python
api.new_coins_listed()
```

* **/coins/top_gainers_losers** - Get the top 30 gainers and losers for a specific duration.

```python
api.gainers_losers()
```

* **/global/market_cap_chart** - Get historical global market cap and volume data.

```python
api.historical_global_market_cap()
```

* **/nfts/markets** - Get list of supported NFTs with market data.
```python
api.nft_market_data()
```

* **/nfts/{id}/market_chart** - Get historical market data of a specific NFT collection by id. 
```python
api.get_nft_collection_historical_market_data(nft_id='bored-ape-yacht-club')
```

* **/nfts/{asset_platform_id}/contract/{contract_address}/market_chart** - Get historical market data of a specific NFT 
  collection by contract address. 
```python
api.nft_historical_data(
   asset_platform_id='ethereum', 
   contract_address='0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d'
)
```

* **/nfts/{id}/tickers** - Get the latest floor price and 24h volume of an NFT collection on each NFT marketplace.

```python
api.nft_market_tickers(nft_id='bored-ape-yacht-club')
```
</details>

<details><summary>enterprise plan (exclusive)</summary>
<p>

* **/coins/{id}/circulating_supply_chart** - Get historical circulating supply data for a coin.

```python
api.coin_circulating_supply_history(coin_id='bitcoin')
```   

* **/coins/{id}/circulating_supply_chart/range** - Get historical circulating supply data for a coin within a date 
  range.

```python
api.coin_circulating_supply_history(coin_id='bitcoin', from_date='12-31-2022', to_date='12-31-2023')
```

* **/coins/{id}/total_supply_chart** - Get historical total supply data for a coin.

```python
api.coin_total_supply_history(coin_id='bitcoin')
```

* **/coins/{id}/total_supply_chart/range** - Get historical total supply data for a coin within a date range.

```python
api.coin_total_supply_history(coin_id='bitcoin', from_date='12-31-2022', to_date='12-31-2023')
```

* **/token_lists/{asset_platform_id}/all.json** - Get list of tokens for a specific blockchain network supported by 
  Ethereum token list standard.

```python
api.all_tokens_list(asset_platform_id='ethereum')
```
</details>

## Running on Docker
You can run `pycgapi` inside a Docker container. Below are the steps to build and run the Docker image:

1. **Build the Docker Image**:

   First, navigate to the root directory of the project in the command prompt and build the Docker image using the 
   following command:

   ```bash
   docker build --no-cache -t pycgapi .
   ```
   
2. **Running the Docker Container**:

   Once the Docker image is built, you can run the Docker container using the following command:
   
   ```bash
   docker run -it pycgapi
   ```

## Testing
To run the test suite with coverage analysis, navigate to the root directory of the project and use the following command:

```bash
coverage run -m unittest discover -s tests
```

This command uses ``coverage`` to run all tests in the tests directory and collect coverage data as specified in the 
.coveragerc file. After running the tests, you can generate a report to see the coverage percentage with:

```bash
coverage report
```

Or, to generate an HTML report showing line-by-line coverage:
```bash
coverage html
```

This will create a new directory named ``htmlcov``. Open the ``index.html`` file in this directory with a web browser to view 
the detailed coverage report.

## Roadmap
- [ ] Add asynchronous functionality to improve performance.

## Contributing
Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## Change Log
Notable changes can be found in the [Change Log](https://github.com/nathanramoscfa/pycgapi/blob/main/CHANGELOG.md). 

## License
`pycgapi` is released under the MIT License. See [LICENSE](https://github.com/nathanramoscfa/pycgapi/LICENSE) file for more details.

## Contact
Find me on [LinkedIn](https://www.linkedin.com/in/nathanramoscfa/) or schedule a meeting with me on 
[Calendly](https://calendly.com/nrcapitalmanagement/pycgapi-meeting). 
