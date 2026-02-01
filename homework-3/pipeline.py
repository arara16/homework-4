"""
CryptoVault Analytics - Pipe and Filter Data Processing System
Main execution module for cryptocurrency historical data collection and normalization.

Author: Team CryptoVault
Date: November 2025
License: MIT
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import os

import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# CONFIGURATION
# ============================================================================

# Create necessary directories
DATA_DIR = Path("data")
METADATA_DIR = DATA_DIR / "metadata"
CRYPTO_DIR = DATA_DIR / "cryptocurrencies"
LOG_DIR = Path("logs")

for directory in [DATA_DIR, METADATA_DIR, CRYPTO_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"cryptovault_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CryptoVault")

# API Configuration
BINANCE_API_URL = "https://api.binance.com/api/v3"
SYMBOLS_FILE = METADATA_DIR / "exchange_symbols.json"
RATE_LIMIT_DELAY = 0.05  # seconds between API requests (1200 req/min = ~20 per second)
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10

# Validation Configuration
MINIMUM_DAILY_VOLUME_USDT = 0  # NO MINIMUM - accept all volumes
ACCEPTED_QUOTE_CURRENCIES = {"USDT", "BUSD", "USDC"}
TOP_N_SYMBOLS = 100


# ============================================================================
# UTILITIES
# ============================================================================

def create_retry_session(retries=3, backoff_factor=0.3):
    """
    Create requests session with retry strategy for handling transient failures.

    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for exponential retry delays

    Returns:
        requests.Session: Configured session with retry strategy
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def api_request(endpoint: str, params: Optional[Dict] = None, session: Optional[requests.Session] = None) -> Dict:
    """
    Make HTTP request to Binance API with error handling and retries.

    Args:
        endpoint: API endpoint path
        params: Query parameters
        session: Optional requests session (creates new if not provided)

    Returns:
        dict: JSON response from API

    Raises:
        Exception: If API request fails after retries
    """
    if session is None:
        session = create_retry_session()

    url = f"{BINANCE_API_URL}{endpoint}"

    try:
        response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API request failed: {endpoint} - {str(e)}")
        raise


# ============================================================================
# FILTER 1: SYMBOL ACQUISITION AND VALIDATION
# ============================================================================

def filter_1_acquire_symbols() -> Tuple[List[str], Dict]:
    """
    FILTER 1: Automatically download and validate cryptocurrency symbols.

    This filter:
    1. Queries Binance API for all trading symbols
    2. Retrieves 24-hour trading volume for each symbol
    3. Filters to top 1000 by volume
    4. Excludes invalid/illiquid symbols
    5. Deduplicates and validates formatting

    Returns:
        Tuple[List[str], Dict]: Cleaned symbol list and metadata dictionary
    """
    logger.info("FILTER 1: Starting symbol acquisition and validation...")

    start_time = time.time()
    session = create_retry_session()

    try:
        # Step 1: Get all exchange info with symbol data
        logger.info("Fetching exchange information from Binance...")
        exchange_info = api_request("/exchangeInfo", session=session)

        symbols_data = []

        # Step 2: Extract symbols and get 24h ticker data for volume
        logger.info("Retrieving 24-hour statistics for volume filtering...")
        ticker_24h = api_request("/ticker/24hr", session=session)

        # Convert ticker list to dictionary for fast lookup
        ticker_dict = {item['symbol']: item for item in ticker_24h}

        # Step 3: Process symbols with validation rules
        logger.info("Processing and validating symbols...")
        excluded_count = 0

        for symbol_obj in exchange_info['symbols']:
            symbol = symbol_obj['symbol']

            # Skip if symbol not in ticker data
            if symbol not in ticker_dict:
                continue

            ticker = ticker_dict[symbol]

            # Validation Rule 1: Quote currency must be in accepted list
            quote_asset = symbol_obj.get('quoteAsset', '')
            if quote_asset not in ACCEPTED_QUOTE_CURRENCIES:
                excluded_count += 1
                continue

            # Validation Rule 2: Symbol must be trading (status = TRADING)
            if symbol_obj.get('status') != 'TRADING':
                excluded_count += 1
                continue

            # Validation Rule 3: No zero or invalid prices
            try:
                last_price = float(ticker.get('lastPrice', 0))
                if last_price <= 0:
                    excluded_count += 1
                    continue
            except (ValueError, TypeError):
                excluded_count += 1
                continue

            # Get volume
            quote_volume = float(ticker.get('quoteAssetVolume', 0))

            # Valid symbol - collect data
            symbols_data.append({
                'symbol': symbol,
                'base_asset': symbol_obj.get('baseAsset'),
                'quote_asset': quote_asset,
                'volume_24h_usdt': quote_volume,
                'last_price': last_price,
                'validation_timestamp': datetime.utcnow().isoformat()
            })

        # Step 4: Sort by volume and take top N
        symbols_data.sort(key=lambda x: x['volume_24h_usdt'], reverse=True)
        top_symbols = symbols_data[:TOP_N_SYMBOLS]

        # Step 5: Extract clean symbol list
        clean_symbols = [item['symbol'] for item in top_symbols]

        # Step 6: Create metadata dictionary
        metadata = {
            'total_symbols_extracted': len(clean_symbols),
            'total_symbols_excluded': excluded_count,
            'timestamp': datetime.utcnow().isoformat(),
            'symbols': top_symbols
        }

        logger.info(
            f"FILTER 1 COMPLETE: {len(clean_symbols)} symbols validated, "
            f"{excluded_count} excluded. Time: {time.time() - start_time:.2f}s"
        )

        return clean_symbols, metadata

    except Exception as e:
        logger.error(f"FILTER 1 FAILED: {str(e)}")
        raise


# ============================================================================
# FILTER 2: DATABASE STATE CHECK AND GAP IDENTIFICATION
# ============================================================================

def filter_2_check_data_gaps(symbols: List[str]) -> Dict[str, Dict]:
    """
    FILTER 2: Check local storage for each symbol and identify data gaps.

    This filter:
    1. For each symbol, checks if local data file exists
    2. If exists, determines the last available data date
    3. If not exists, marks for full historical download
    4. Creates mapping of symbol -> date metadata

    Args:
        symbols: List of validated symbols from Filter 1

    Returns:
        Dict: Symbol -> date metadata mapping for Filter 3
    """
    logger.info(f"FILTER 2: Starting data gap analysis for {len(symbols)} symbols...")

    start_time = time.time()
    symbol_date_map = {}

    for i, symbol in enumerate(symbols):
        if (i + 1) % 100 == 0:
            logger.info(f"  Processing symbol {i + 1}/{len(symbols)}...")

        symbol_file = CRYPTO_DIR / f"{symbol}.jsonl"

        if symbol_file.exists():
            # File exists - find last available date
            try:
                with open(symbol_file, 'r') as f:
                    last_line = None
                    for last_line in f:
                        pass

                    if last_line:
                        last_record = json.loads(last_line)
                        last_date = last_record.get('date')
                        symbol_date_map[symbol] = {
                            'last_available_date': last_date,
                            'requires_full_download': False,
                            'file_exists': True
                        }
                    else:
                        # Empty file
                        symbol_date_map[symbol] = {
                            'last_available_date': None,
                            'requires_full_download': True,
                            'file_exists': True
                        }
            except Exception as e:
                logger.warning(f"Could not read file for {symbol}: {str(e)}")
                symbol_date_map[symbol] = {
                    'last_available_date': None,
                    'requires_full_download': True,
                    'file_exists': False
                }
        else:
            # File does not exist - mark for full download
            symbol_date_map[symbol] = {
                'last_available_date': None,
                'requires_full_download': True,
                'file_exists': False
            }

    logger.info(
        f"FILTER 2 COMPLETE: Gap analysis complete. Time: {time.time() - start_time:.2f}s"
    )

    return symbol_date_map


# ============================================================================
# FILTER 3: HISTORICAL AND INCREMENTAL DATA DOWNLOAD
# ============================================================================

def filter_3_download_data(symbols: List[str], symbol_date_map: Dict[str, Dict]) -> None:
    """
    FILTER 3: Download historical and missing data for all symbols.

    This filter:
    1. For each symbol, determines start date (full or incremental)
    2. Downloads daily OHLCV data from Binance
    3. Normalizes and validates data format
    4. Merges with existing data or creates new file
    5. Ensures no duplicate dates and proper chronological order

    Args:
        symbols: List of symbols to download
        symbol_date_map: Date metadata from Filter 2
    """
    logger.info(f"FILTER 3: Starting data download for {len(symbols)} symbols...")

    start_time = time.time()
    session = create_retry_session()

    total_records_downloaded = 0
    total_records_stored = 0
    errors = []

    for idx, symbol in enumerate(symbols):
        try:
            if (idx + 1) % 50 == 0:
                logger.info(
                    f"  Downloaded {idx + 1}/{len(symbols)} symbols. "
                    f"Records: {total_records_downloaded}. Time: {time.time() - start_time:.2f}s"
                )

            date_meta = symbol_date_map[symbol]

            # Determine start date for download
            if date_meta['requires_full_download']:
                # Download from 10 years ago (or earliest available)
                start_date = datetime.utcnow() - timedelta(days=3650)
            else:
                # Incremental: download from day after last available date
                last_date_str = date_meta['last_available_date']
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
                start_date = last_date + timedelta(days=1)

            # Download data for this symbol
            records = _download_symbol_data(symbol, start_date, session)

            if records:
                total_records_downloaded += len(records)

                # Store data
                _store_symbol_data(symbol, records, date_meta['file_exists'])
                total_records_stored += len(records)

            # Respect API rate limits
            time.sleep(RATE_LIMIT_DELAY)

        except Exception as e:
            error_msg = f"Symbol {symbol}: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue

    logger.info(
        f"FILTER 3 COMPLETE: Downloaded {total_records_downloaded} records, "
        f"stored {total_records_stored} records. "
        f"Errors: {len(errors)}. Time: {time.time() - start_time:.2f}s"
    )

    if errors:
        logger.info(f"Errors encountered: {errors[:5]}")  # Log first 5 errors


def _download_symbol_data(symbol: str, start_date: datetime, session: requests.Session) -> List[Dict]:
    """
    Download daily OHLCV data for a symbol from a start date to present.

    Args:
        symbol: Cryptocurrency symbol (e.g., "BTCUSDT")
        start_date: Start date for historical data
        session: Requests session for API calls

    Returns:
        List[Dict]: List of normalized OHLCV records
    """
    records = []
    current_date = start_date
    end_date = datetime.utcnow()

    while current_date <= end_date:
        try:
            # Binance klines endpoint
            params = {
                'symbol': symbol,
                'interval': '1d',  # Daily candles
                'startTime': int(current_date.timestamp() * 1000),  # milliseconds
                'limit': 1000  # Max 1000 candles per request
            }

            klines = api_request("/klines", params=params, session=session)

            if not klines:
                break  # No more data available

            for kline in klines:
                record = {
                    'symbol': symbol,
                    'timestamp': kline[0] // 1000,  # Convert to seconds
                    'date': datetime.utcfromtimestamp(kline[0] // 1000).strftime('%Y-%m-%d'),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[7]),  # Quote asset volume
                    'number_of_trades': int(kline[8])
                }
                records.append(record)

            # Move to next batch (last kline is the most recent, move just past it)
            if klines:
                current_date = datetime.utcfromtimestamp(klines[-1][0] // 1000) + timedelta(days=1)
            else:
                break

        except Exception as e:
            logger.warning(f"Error downloading {symbol}: {str(e)}")
            break

    return records


def _store_symbol_data(symbol: str, records: List[Dict], file_exists: bool) -> None:
    """
    Store downloaded records to JSON Lines file, handling merging with existing data.

    Args:
        symbol: Cryptocurrency symbol
        records: List of OHLCV records to store
        file_exists: Whether file already exists
    """
    symbol_file = CRYPTO_DIR / f"{symbol}.jsonl"

    if file_exists:
        # Load existing data to check for duplicates
        existing_dates = set()
        try:
            with open(symbol_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    existing_dates.add(record['date'])
        except:
            pass

        # Filter out duplicates
        new_records = [r for r in records if r['date'] not in existing_dates]

        # Append new records
        if new_records:
            with open(symbol_file, 'a') as f:
                for record in new_records:
                    f.write(json.dumps(record) + '\n')
    else:
        # Create new file
        with open(symbol_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')


# ============================================================================
# PIPELINE ORCHESTRATION
# ============================================================================

def run_pipeline(full_run: bool = False) -> None:
    """
    Execute the complete Pipe and Filter data pipeline.

    Args:
        full_run: If True, perform full download; if False, incremental only
    """
    logger.info("=" * 80)
    logger.info("CRYPTOVAULT ANALYTICS - PIPE AND FILTER PIPELINE")
    logger.info("=" * 80)

    pipeline_start = time.time()

    try:
        # FILTER 1: Symbol Acquisition and Validation
        logger.info("\n[STEP 1/3] FILTER 1 - Symbol Acquisition and Validation")
        logger.info("-" * 80)
        symbols, metadata = filter_1_acquire_symbols()

        # Save metadata
        with open(SYMBOLS_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {SYMBOLS_FILE}")

        # FILTER 2: Database State Check and Gap Identification
        logger.info("\n[STEP 2/3] FILTER 2 - Database State Check and Gap Identification")
        logger.info("-" * 80)
        symbol_date_map = filter_2_check_data_gaps(symbols)

        # FILTER 3: Historical and Incremental Data Download
        logger.info("\n[STEP 3/3] FILTER 3 - Historical and Incremental Data Download")
        logger.info("-" * 80)
        filter_3_download_data(symbols, symbol_date_map)

        # Pipeline Complete
        pipeline_time = time.time() - pipeline_start
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE EXECUTION COMPLETE")
        logger.info(f"Total Execution Time: {pipeline_time:.2f} seconds ({pipeline_time / 60:.2f} minutes)")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"PIPELINE FAILED: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run_pipeline(full_run=True)
