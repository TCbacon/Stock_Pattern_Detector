from flask import Flask, render_template, jsonify, request
import talib
import yfinance as yf
from patterns import candlestick_patterns
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import re
import threading

app = Flask(__name__)

@dataclass
class PatternDetect:

    detected_patterns_dict: dict = field(default_factory=dict)
    rsi_period: int = 14 
    interval: int = 60
    end_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d')

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
        
        stock_dict = self.get_stock_symbols()

        for symbol in stock_dict:

            df = yf.download(symbol, start=self.start_date, end=self.end_date)
            rsi = self.compute_RSI(symbol)
            computed_rsi = f"RSI: {rsi}"
            current_price = self.get_current_price(symbol)

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
                    print('failed on symbol: {}'.format(symbol))
        
        return self.detected_patterns_dict

    def compute_RSI(self, symbol):
        try:
            data = yf.download(symbol, period="1d", interval="1m")
            rsi = talib.RSI(data['Close'], timeperiod=self.rsi_period)[-1]
            rsi = round(rsi, 2)
            return rsi
        except:
            return -1

    def get_current_price(self, symbol):

        try:
            ticker_data = yf.Ticker(symbol)
            data = ticker_data.history()
            last_quote = data['Close'].iloc[-1]
            
            last_quote = round(last_quote, 3)
            return last_quote
        except Exception as e:
            print(e)
            return -1

    def run_interval_detection(self):
        thread = threading.Timer(self.interval, self.run_interval_detection)
        thread.start()
        self.detect_patterns()

    def get_stock_data(self):
            return self.detected_patterns_dict 
    
    def get_default_settings(self):
        return {"start_date": self.start_date, "end_date": self.end_date, "rsi_period": self.rsi_period, "interval":self.interval}
    
    def update_user_input(self, data):

        try:
            interval = int(data['interval'])
            rsi_period = int(data['rsi_period'])
            stock_period = int(data['stock_period'])

            if interval < 10 or interval > 10000 or rsi_period < 1 or rsi_period > 99 or stock_period < 1 or stock_period > 10000:
                return jsonify({"message": "Please enter valid numbers"})

            self.interval = interval
            self.rsi_period = rsi_period
            self.stock_period = stock_period

            self.end_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
            self.start_date = (datetime.now() - timedelta(days=self.stock_period)).strftime('%Y-%m-%d')

            return jsonify({"message": "Updated successfully", "start_date": self.start_date, "end_date": self.end_date, "rsi_period": self.rsi_period, "interval":self.interval})
        except:
            return jsonify({"message": "Something went wrong..."})

pattern = PatternDetect()

@app.route('/get_default_settings')
def get_default_settings():
    return pattern.get_default_settings()

@app.route('/user_input', methods=['POST'])
def update_user_input():
    data = request.get_json()
    return pattern.update_user_input(data)

@app.route("/get_latest_data")
def get_latest_data():
   return pattern.get_stock_data()

@app.route("/run_interval_detection")
def run_interval_detection():
    pattern.run_interval_detection()
    result = {'message': 'Running...'}
    return jsonify(result)

@app.route("/")
def main():

    try:
        return render_template("index.html")
    except Exception as e:
        return "Oops, 500 Internal Server Error"
    

if __name__ == "__main__":
    app.run(debug=True, port="5000")
