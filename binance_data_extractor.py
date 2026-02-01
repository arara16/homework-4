import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

class BinanceDataExtractor:
    """Extract real-time and historical data from Binance API"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.data_dir = Path('data/cryptocurrencies')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_klines(self, symbol, interval='1h', limit=1000):
        """Get historical kline data from Binance"""
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(f"{self.base_url}/klines", params=params, timeout=10)
            if response.status_code == 200:
                klines = response.json()
                
                # Convert to OHLCV format
                ohlcv_data = []
                for kline in klines:
                    ohlcv_data.append({
                        'time': kline[0],
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[5]),
                        'quote_volume': float(kline[7]),
                        'count': int(kline[8])
                    })
                return ohlcv_data
            else:
                print(f"Error fetching klines for {symbol}: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception fetching klines for {symbol}: {e}")
            return []
    
    def get_24hr_ticker(self, symbol):
        """Get 24hr ticker data from Binance"""
        try:
            response = requests.get(f"{self.base_url}/ticker/24hr", params={'symbol': symbol}, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching ticker for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching ticker for {symbol}: {e}")
            return None
    
    def save_symbol_data(self, symbol, data):
        """Save symbol data to JSONL file"""
        file_path = self.data_dir / f"{symbol}.jsonl"
        
        # Convert to JSONL format
        jsonl_data = [json.dumps(record) for record in data]
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(jsonl_data))
        
        print(f"Saved {len(data)} records for {symbol}")
    
    def extract_all_symbols(self):
        """Extract data for all popular symbols"""
        # Popular cryptocurrency symbols
        symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT',
            'LINKUSDT', 'UNIUSDT', 'LTCUSDT', 'ATOMUSDT', 'XLMUSDC'
        ]
        
        for symbol in symbols:
            print(f"Extracting data for {symbol}...")
            
            # Get historical data
            historical_data = self.get_klines(symbol, '1h', 1000)
            
            if historical_data:
                # Get current 24hr ticker to add latest info
                ticker = self.get_24hr_ticker(symbol)
                if ticker:
                    # Add current ticker data as the latest record
                    latest_record = {
                        'time': int(datetime.now().timestamp() * 1000),
                        'open': float(ticker['openPrice']),
                        'high': float(ticker['highPrice']),
                        'low': float(ticker['lowPrice']),
                        'close': float(ticker['lastPrice']),
                        'volume': float(ticker['volume']),
                        'quote_volume': float(ticker['quoteVolume']),
                        'count': int(ticker['count'])
                    }
                    historical_data.append(latest_record)
                
                # Save to file
                self.save_symbol_data(symbol, historical_data)
            else:
                print(f"No data extracted for {symbol}")
    
    def update_live_data(self):
        """Update only the latest data for all symbols"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'LINKUSDC', 'XLMUSDC']
        
        for symbol in symbols:
            file_path = self.data_dir / f"{symbol}.jsonl"
            
            if file_path.exists():
                # Read existing data
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Get latest ticker data
                ticker = self.get_24hr_ticker(symbol)
                if ticker:
                    # Create new latest record
                    latest_record = {
                        'time': int(datetime.now().timestamp() * 1000),
                        'open': float(ticker['openPrice']),
                        'high': float(ticker['highPrice']),
                        'low': float(ticker['lowPrice']),
                        'close': float(ticker['lastPrice']),
                        'volume': float(ticker['volume']),
                        'quote_volume': float(ticker['quoteVolume']),
                        'count': int(ticker['count'])
                    }
                    
                    # Add to existing data
                    lines.append(json.dumps(latest_record) + '\n')
                    
                    # Save back
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                    
                    print(f"Updated live data for {symbol}")

if __name__ == "__main__":
    extractor = BinanceDataExtractor()
    
    print("🚀 Extracting data from Binance API...")
    
    # Extract all symbols (this will take a few minutes)
    extractor.extract_all_symbols()
    
    print("✅ Data extraction complete!")
    print(f"📁 Data saved to: {extractor.data_dir}")
