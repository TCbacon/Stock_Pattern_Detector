from flask import Flask, render_template, jsonify
import talib
import yfinance as yf
import pandas
from patterns import candlestick_patterns
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import re
import threading

app = Flask(__name__)

@dataclass
class PatternDetect:

    time_period: int = 14 
    detected_patterns_dict: dict = field(default_factory=dict)


    def get_stock_symbols(self):
        
        stock_dict = {}
    
        with open('datasets/symbols.csv', 'r') as f:
            lines = f.readlines()
            for stock in lines:
                tokens = re.split(",\s?", stock, maxsplit=1)
                if len(tokens) == 2:
                    stock_dict[tokens[0]] = tokens[1]
        return stock_dict


    @app.route("/detect_patterns")
    def detect_patterns(self):
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        stock_dict = self.get_stock_symbols()

        for symbol in stock_dict:

            df = yf.download(symbol, start=start_date, end=end_date)
            rsi = self.compute_RSI(symbol)
            computed_rsi = f"RSI: {rsi}"
            current_price = self.get_current_price(symbol)
            print("computing pattern")

            for sym, pat in candlestick_patterns.items():

                dynamic_pattern_call = getattr(talib, sym)

                try:
                    results = dynamic_pattern_call(df['Open'], df['High'], df['Low'], df['Close'])
                    last = results.tail(1).values[0]
                    if last > 0:
                        self.detected_patterns_dict[symbol] = [current_price, 'bullish', pat, computed_rsi]
                        break
                    elif last < 0:
                        self.detected_patterns_dict[symbol] = [current_price, 'bearish', pat, computed_rsi]
                        break
                    else:
                        self.detected_patterns_dict[symbol] = [current_price, 'flat', '-', computed_rsi]
                except Exception as e:
                    print('failed on filename: {}'.format(symbol))
        

        return self.detected_patterns_dict

    def compute_RSI(self, symbol):
     
        data = yf.download(symbol, period="1d", interval="1m")
        rsi = talib.RSI(data['Close'], timeperiod=self.time_period)[-1]
        rsi = round(rsi, 2)
        return rsi

    def get_current_price(self, symbol):
        try:
            ticker_data = yf.Ticker(symbol)
            data = ticker_data.history()
            last_quote = data['Close'].iloc[-1]
            last_quote = round(last_quote, 2)
            print(symbol, last_quote)
            return last_quote
        except:
            return -1

    def get_stock_data(self):
        return self.detected_patterns_dict

    def run_interval_detection(self):
        
        interval = 300
        thread = threading.Timer(interval, self.run_interval_detection)
        thread.start()
        self.detect_patterns()

  
pattern = PatternDetect()

@app.route("/get_latest_data")
def get_latest_data():
   return pattern.get_stock_data()

@app.route("/run_interval_detection")
def run_interval_detection():

    current_time = datetime.now().time()
    today = date.today()
    weekday = today.weekday()
    start_time: datetime = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0).time()
    end_time: datetime = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0).time()
    result = ""

    if current_time >= start_time and current_time <= end_time and weekday < 5:
        pattern.run_interval_detection()
    else:
        result = {
        'message': 'Market closed'
        }

    return jsonify(result)
    

@app.route("/")
def main():

    try:
        patterns = {"AMC":[4.18,"bearish","Short Line Candle",
                    "RSI: 42.85622009571722"],
                    "EBAY":[42.06,"-","-","RSI: 43.880011887433476"],
                    "META":[195.61,"bearish","Closing Marubozu","RSI: 21.5661590027824"],
                    "NDAQ":[52.75,"bearish","Spinning Top","RSI: 26.01557634523849"],
                    "NFLX":[303.5,"bearish","Belt-hold","RSI: 62.466557010345426"],
                    "NKE":[120.39,"-","-","RSI: 57.00969318529285"],
                    "SPY":[389.99,"bearish","Harami Pattern","RSI: 51.83827279539456"],
                    "TSLA":[180.13,"bearish","Engulfing Pattern","RSI: 57.383609501224534"],
                    "U":[28.32,"bearish","Belt-hold","RSI: 54.99652768469413"],
                    "UVXY":[6.42,"-","-","RSI: 48.62245083788231"],
                    "V":[217.39,"bullish","Belt-hold","RSI: 56.85365000076771"]
                }
        return render_template("index.html", patterns=patterns)
    except Exception as e:
        return "Oops, 500 Internal Server Error"
    

if __name__ == "__main__":
    app.run(debug=True, port="5000")
