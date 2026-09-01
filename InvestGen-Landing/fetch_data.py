import psxdata
import pandas as pd
import numpy as np
import json
import os
import datetime

# Top 5 PSX Tickers with mock details
TICKERS = {
    "ENGRO": {"name": "Engro Corporation Limited", "base": 300, "shares": 500_000_000},
    "LUCK": {"name": "Lucky Cement Limited", "base": 850, "shares": 300_000_000},
    "HUBC": {"name": "Hub Power Company Limited", "base": 130, "shares": 1_200_000_000},
    "SYS": {"name": "Systems Limited", "base": 420, "shares": 250_000_000},
    "MEBL": {"name": "Meezan Bank Limited", "base": 180, "shares": 1_500_000_000}
}

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def mock_genai_logic(rsi, change):
    if rsi > 60 and change > 0:
        return "Trending Bullish", "Strong upward momentum. HMM confirms stable trend. MACD crossover positive.", 92, "No critical counter-evidence found."
    elif rsi < 40 and change < 0:
        return "Trending Bearish", "Downward pressure. HMM detects high volatility sell-off.", 85, "Analog matches 2022 bear run."
    else:
        return "Sideways", "Market in consolidation phase. Support holding firm.", 65, "Conflicting signals in recent analogs."

def generate_mock_ohlcv(base_price, days=90):
    dates = pd.date_range(end=datetime.date.today(), periods=days)
    np.random.seed(int(base_price))
    
    returns = np.random.normal(0.001, 0.02, days)
    price = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame(index=dates)
    df['Close'] = price
    df['Open'] = df['Close'].shift(1).fillna(base_price)
    
    vol = df['Close'] * 0.015
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.abs(np.random.normal(0, vol))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.abs(np.random.normal(0, vol))
    df['Volume'] = np.random.randint(1_000_000, 10_000_000, days)
    
    return df

def generate_market_data():
    market_data = {
        "top_5": [],
        "all_stocks": [],
        "market_overview": {
            "regime": "Trending Bullish",
            "description": "The KSE-100 is operating in a low-volatility, trending bullish state as identified by our simulated HMM.",
            "leading_sectors": [{"name": "Fertilizer", "status": "Strong"}],
            "lagging_sectors": [{"name": "Technology", "status": "Weak"}],
            "index_chart": [],
            "contributors": [
                {"ticker": "MEBL", "points": 62.87, "type": "positive"},
                {"ticker": "PSO", "points": 48.12, "type": "positive"},
                {"ticker": "HBL", "points": 35.93, "type": "positive"},
                {"ticker": "BAHL", "points": 34.90, "type": "positive"},
                {"ticker": "OGDC", "points": -31.27, "type": "negative"},
                {"ticker": "ENGRO", "points": -26.28, "type": "negative"},
                {"ticker": "FFC", "points": -23.53, "type": "negative"}
            ],
            "commodities": {
                "gold": {"price": 4119.80, "change": 1.75},
                "silver": {"price": 59.21, "change": 2.81},
                "copper": {"price": 6.61, "change": 2.64},
                "crude_oil": {"price": 81.29, "change": -3.99}
            }
        },
        "stocks": {}
    }

    # Fetch ALL Stocks (Fast Single Call using ALLSHR Index)
    print("Fetching ALLSHR index constituents for All Stocks page (Full Market)...")
    try:
        all_df = psxdata.indices("ALLSHR")
        for _, row in all_df.iterrows():
            sym = str(row['symbol'])
            current_str = str(row['current']).replace(',', '')
            change_str = str(row['change_pct']).replace('%', '').replace(',', '')
            market_data["all_stocks"].append({
                "ticker": sym,
                "name": str(row['name']),
                "price": float(current_str) if current_str != 'nan' else 0.0,
                "change": float(change_str) if change_str != 'nan' else 0.0,
                "sector": "KSE100"
            })
    except Exception as e:
        print(f"Error fetching KSE100 indices: {e}")

    # Generate KSE-100 Index Mock Data Chart (as per plan)
    index_df = generate_mock_ohlcv(75000, 180)
    for date, row in index_df.iterrows():
        market_data["market_overview"]["index_chart"].append({
            "time": date.strftime('%Y-%m-%d'),
            "open": round(float(row['Open']), 2),
            "high": round(float(row['High']), 2),
            "low": round(float(row['Low']), 2),
            "close": round(float(row['Close']), 2)
        })

    start_date = (datetime.date.today() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = datetime.date.today().strftime('%Y-%m-%d')

    for ticker, info in TICKERS.items():
        name = info["name"]
        shares = info["shares"]
        print(f"Fetching {ticker} historicals via psxdata...")
        try:
            df = psxdata.stocks(ticker, start=start_date, end=end_date)
            
            if df is None or df.empty:
                print(f"No data for {ticker}, using fallback mock generator...")
                df = generate_mock_ohlcv(info["base"])
            else:
                df.columns = [c.capitalize() for c in df.columns]

            df['RSI'] = calculate_rsi(df)
            current_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            current_vol = int(df['Volume'].iloc[-1]) if 'Volume' in df.columns else np.random.randint(1000000, 5000000)
            change_pct = ((current_close - prev_close) / prev_close) * 100
            current_rsi = float(df['RSI'].iloc[-1])
            
            regime, ai_summary, confidence, disconf = mock_genai_logic(current_rsi, change_pct)
            
            # LightweightCharts requires data to be sorted chronologically
            if 'date' in df.columns:
                df = df.sort_values('date')
            elif 'Date' in df.columns:
                df = df.sort_values('Date')
            else:
                df = df.sort_index()
                
            chart_data = []
            for idx, row in df.iterrows():
                # Get the actual date string whether it's in the index or a column
                if 'date' in df.columns:
                    time_str = str(row['date']).split(' ')[0]
                elif 'Date' in df.columns:
                    time_str = str(row['Date']).split(' ')[0]
                else:
                    time_str = idx.strftime('%Y-%m-%d') if isinstance(idx, pd.Timestamp) else str(idx)
                    
                chart_data.append({
                    "time": time_str,
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2)
                })
            
            market_cap = current_close * shares
            
            stock_info = {
                "ticker": ticker,
                "name": name,
                "price": round(current_close, 2),
                "change": round(change_pct, 2),
                "volume": f"{current_vol:,}",
                "market_cap": f"Rs {market_cap / 1_000_000_000:.2f} Billion",
                "regime": regime,
                "confidence": confidence,
                "rsi": round(current_rsi, 1) if not pd.isna(current_rsi) else 50.0,
                "macd": "Crossover UP" if change_pct > 0 else "Neutral",
                "pe": 8.5,
                "ai_summary": ai_summary,
                "disconfirmation": disconf,
                "chart_data": chart_data
            }
            
            market_data["stocks"][ticker] = stock_info
            
            market_data["top_5"].append({
                "ticker": ticker,
                "name": name,
                "price": round(current_close, 2),
                "change": round(change_pct, 2),
                "regime": regime,
                "confidence": confidence
            })
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    os.makedirs("data", exist_ok=True)
    with open("data/market_data.json", "w") as f:
        json.dump(market_data, f, indent=4)
    print("market_data.json generated successfully!")

if __name__ == "__main__":
    generate_market_data()
