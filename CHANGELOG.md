# Changelog

All notable changes to `pycgapi` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to 
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Asynchronous functionality for enhanced performance (planned).

## [0.1.1] - 2024-01-09

### Added
- Automated GitHub workflow for Pypi package release.
- Separation of different GitHub workflows into their individual `.yml` files.
- Creation of `__version__.py` to maintain a single source of truth for the project's version number.
- Updates to README.md and index.rst for correcting hyperlinks to `examples`.
- Inclusion of `sphinx` in `requirements.txt` for documentation support.

## [0.1.0] - 2024-01-08

### Added
- Initial release of `pycgapi`, an unofficial Python wrapper for the CoinGecko API (V3).
- Simplified endpoint access for easy integration with Python applications.
- Comprehensive data access for over thousands of cryptocurrencies.
- Enhanced functionality for Pro users with access to exclusive data sets.
- Support for multiple categories including coins, exchanges, derivatives, DeFi, and NFTs.
- Historical data retrieval and global cryptocurrency statistics.
- Efficient rate limit management and comprehensive error handling.
- Real-time data updates for timely analysis and decision-making.
- Integration with `keyring` for secure API key storage.
- Docker support for containerized application deployment.
- Extensive documentation for all methods and usage examples.
- Roadmap outlining future enhancements.
- License file under MIT License.
- Contribution guidelines for community involvement.

### Fixed
- Comprehensive testing for all functionalities ensuring robust performance.
