import sys
from datetime import datetime, timedelta
import MetaTrader5 as mt5

# Import directly from the dataflows structure
from tradingagents.dataflows.mt5_data import get_MT5_data, get_stock_stats_indicators_mt5

def test_mt5_live_data():
    symbol = "GOLD"
    interval = "15m"
    
    # Calculate dates just like the agent does
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5) # 5 days lookback for 15m
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"==========================================")
    print(f" TESTING MT5 LIVE DATA EXTRACTION")
    print(f" Symbol: {symbol}")
    print(f" Interval: {interval}")
    print(f" From: {start_str} To: {end_str}")
    print(f"==========================================")
    
    # Check MT5 connection and live Ask/Bid directly first
    if not mt5.initialize():
         print("initialize() failed, error code =", mt5.last_error())
         return
         
    lastticket = mt5.symbol_info_tick(symbol)
    if lastticket:
        print(f"\n--- Direct Live Tick (Real-Time) ---")
        print(f"   Time: {datetime.fromtimestamp(lastticket.time)}")
        print(f"   Bid:  {lastticket.bid}")
        print(f"   Ask:  {lastticket.ask}")
        print(f"   Last: {lastticket.last}")
    else:
        print(f"Could not fetch symbol_info_tick for {symbol}")
    
    
    # Fetch Data using the Agent's function
    print("\n==========================================")
    print("Fetching OHLCV Data (via Agent's mt5_data.py)...")
    stock_data = get_MT5_data(symbol, start_str, end_str, interval=interval)
    
    # Print only the last 15 lines of the CSV output to check the latest price
    lines = stock_data.split('\n')
    print("... (Showing latest 10 candles) ...")
    for line in lines[-12:]:
        if line.strip():
            print(line)
            
    print("\n==========================================")
    print("Fetching Technical Indicators (e.g., RSI)...")
    try:
        rsi_data = get_stock_stats_indicators_mt5(symbol, "rsi", end_str, look_back_days=5, interval=interval)
        print(rsi_data)
    except Exception as e:
        print(f"Error fetching indicators: {e}")
        
    print("\n==========================================")
    print("Fetching Technical Indicators (e.g., 50 SMA)...")
    try:
        sma_data = get_stock_stats_indicators_mt5(symbol, "close_50_sma", end_str, look_back_days=5, interval=interval)
        print(sma_data)
    except Exception as e:
        print(f"Error fetching indicators: {e}")

if __name__ == "__main__":
    test_mt5_live_data()
