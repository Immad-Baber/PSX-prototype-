import yfinance as yf
import json
import os

def fetch_psx_data():
    symbols = {
        "ENGRO": "ENGRO.KA",
        "SYS": "SYS.KA",
        "LUCK": "LUCK.KA",
        "HUBC": "HUBC.KA",
        "OGDC": "OGDC.KA",
        "MEBL": "MEBL.KA",
        "POL": "POL.KA",
        "FFC": "FFC.KA",
        "MCB": "MCB.KA",
        "UBL": "UBL.KA"
    }

    data_list = []

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            info = stock.info

            if hist.empty:
                print(f"Could not fetch data for {name}")
                continue

            last_quote = hist.iloc[-1]
            prev_quote = hist.iloc[-2] if len(hist) > 1 else last_quote

            current_price = last_quote['Close']
            prev_price = prev_quote['Close']
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price else 0

            chart_data = hist['Close'].tolist()

            data_list.append({
                "symbol": name,
                "name": info.get('longName', name),
                "sector": info.get('sector', 'Unknown'),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": int(last_quote['Volume']),
                "marketCap": info.get('marketCap', 0),
                "peRatio": info.get('trailingPE', 0),
                "chart": [round(val, 2) for val in chart_data]
            })
            print(f"Fetched {name} successfully.")
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    output_path = os.path.join(os.path.dirname(__file__), 'psx_data.json')
    with open(output_path, 'w') as f:
        json.dump(data_list, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    fetch_psx_data()
