# module_mapping.py

# Mapping of module names to class names with paths
module_to_class = {
    'asset_platforms': ('AssetPlatforms', 'asset_platforms'),
    'categories': ('Categories', 'categories'),
    'coins': ('Coins', 'coins'),
    'companies': ('Companies', 'companies'),
    'contract': ('Contract', 'contract'),
    'derivatives': ('Derivatives', 'derivatives'),
    'exchange_rates': ('ExchangeRates', 'exchange_rates'),
    'exchanges': ('Exchanges', 'exchanges'),
    'global_data': ('GlobalData', 'global_data'),
    'key': ('APIKeyData', 'key'),
    'nft': ('NFTData', 'nft'),
    'ohlc_data': ('OHLCData', 'ohlc_data'),
    'ping': ('Ping', 'ping'),
    'search': ('Search', 'search'),
    'simple': ('Simple', 'simple'),
    'trending': ('Trending', 'trending'),

    # Onchain modules with subdirectory paths
    'dexes': ('Dexes', 'onchain.dexes'),
    'networks': ('Networks', 'onchain.networks'),
    'ohlcv': ('OHLCV', 'onchain.ohlcv'),
    'pools': ('Pools', 'onchain.pools'),
    'simple_onchain': ('SimpleOnChain', 'onchain.simple'),
    'tokens': ('Tokens', 'onchain.tokens'),
    'trades': ('Trades', 'onchain.trades')
}
