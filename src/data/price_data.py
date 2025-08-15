import pandas as pd
from datetime import datetime, timedelta
import requests

def fetch_bitcoin_data(symbol="BTC-USD", period="30d", interval="30m"):
    """Fetch Bitcoin data from Coinbase Exchange API."""
    try:
        # Get current Bitcoin price from Coinbase
        current_url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        current_response = requests.get(current_url, timeout=10)
        
        if current_response.status_code != 200:
            print(f"❌ Current price: HTTP {current_response.status_code}")
            return pd.DataFrame()
        
        current_data = current_response.json()
        current_price = float(current_data['data']['amount'])
        
        # Get historical data from Coinbase Exchange API
        # Calculate date range for historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        # Convert to date format for the API
        start_date = start_time.strftime('%Y-%m-%d')
        end_date = end_time.strftime('%Y-%m-%d')
        
        # Use the Coinbase Exchange API endpoint (no authentication required)
        # Granularity: 86400 = 1 day, 3600 = 1 hour, 300 = 5 minutes
        historical_url = f"https://api.exchange.coinbase.com/products/BTC-USD/candles?start={start_date}&end={end_date}&granularity=86400"
        
        # Make the request directly
        historical_response = requests.get(historical_url, timeout=10)
        
        if historical_response.status_code == 200:
            candles = historical_response.json()
            
            if candles and isinstance(candles, list) and len(candles) > 0:
                # Vectorized processing: [time, low, high, open, close, volume]
                columns = ['time', 'Low', 'High', 'Open', 'Close', 'Volume']
                filtered = [c for c in candles if isinstance(c, (list, tuple)) and len(c) == 6]

                if filtered:
                    df = pd.DataFrame(filtered, columns=columns)
                    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
                    numeric_cols = ['Low', 'High', 'Open', 'Close', 'Volume']
                    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
                    df = df.dropna(subset=numeric_cols)
                    df.set_index('time', inplace=True)
                    return df
        
        print("❌ Failed to fetch historical data")
        return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return pd.DataFrame()

def calculate_atr(data, period=14):
    """Calculate Average True Range (ATR) indicator."""
    if data.empty or len(data) < period:
        print(f"❌ Need at least {period} data points for ATR")
        return pd.Series()
    
    try:
        # Calculate True Range
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
        
    except Exception as e:
        print(f"❌ ATR calculation failed: {e}")
        return pd.Series()

def get_latest_price_and_atr(symbol="BTC-USD"):
    """Get latest Bitcoin price and ATR - main function called every 30 minutes."""
    data = fetch_bitcoin_data(symbol, period="30d", interval="30m")
    
    if data.empty:
        return {"error": "No data available"}
    
    atr = calculate_atr(data)
    if atr.empty:
        return {"error": "ATR calculation failed"}
    
    latest_price = data['Close'].iloc[-1]
    latest_atr = atr.iloc[-1]
    
    # Calculate price change
    if len(data) > 1:
        price_change = ((latest_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
    else:
        price_change = 0.0
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "price": latest_price,
        "price_change_percent": price_change,
        "atr": latest_atr,
        "volume": data['Volume'].iloc[-1] if 'Volume' in data.columns else 0,
        "high": data['High'].iloc[-1],
        "low": data['Low'].iloc[-1]
    }
    
    print(f"📊 Market: ${latest_price:,.2f} ({price_change:+.2f}%) | ATR: ${latest_atr:,.2f}")
    return result

if __name__ == "__main__":
    print("Testing Bitcoin data module...")
    result = get_latest_price_and_atr()
    print(f"\nResult: {result}")
