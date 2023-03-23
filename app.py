from flask import Flask, render_template, jsonify, request
import talib
import yfinance as yf
from patterns import candlestick_patterns
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
import threading

app = Flask(__name__)

@dataclass
class PatternDetect:

    detected_patterns_dict: dict = field(default_factory=dict)
    rsi_period: int = 14 
    interval: int = 40
    end_date: str = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date: str = (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d')
    stock_file: list = field(default_factory=list)
    mime_type: str = "text/csv"
    file_name: str = "None"

    def get_stock_symbols(self):
        symbols_dict = {}
        for line in self.stock_file:
            line = line.decode('utf-8')
            tokens = re.split(",\s?", line, maxsplit=1)
            if len(tokens) == 2:
                symbols_dict[tokens[0]] = tokens[1]
        
        return symbols_dict

    @app.route("/detect_patterns")
    def detect_patterns(self):
        
        symbols_dict = self.get_stock_symbols()
        temp_detected_patterns_dict = {}

        for symbol in symbols_dict:

            ticker = yf.Ticker(symbol)
            hist  = ticker.history(period="1d")
            if hist.empty:
                continue

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
                        temp_detected_patterns_dict[symbol] = [symbols_dict[symbol], current_price, 'bullish', pat, computed_rsi]
                        break
                    elif last < 0:
                        temp_detected_patterns_dict[symbol] = [symbols_dict[symbol], current_price, 'bearish', pat, computed_rsi]
                        break
                    else:
                        temp_detected_patterns_dict[symbol] = [symbols_dict[symbol], current_price, 'flat', '-', computed_rsi]
                except Exception as e:
                    print('failed on symbol: {}'.format(symbol))
        
        self.detected_patterns_dict = temp_detected_patterns_dict
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
            return -1

    def run_interval_detection(self):
        thread = threading.Timer(self.interval, self.run_interval_detection)
        thread.start()
        self.detect_patterns()

    def get_stock_data(self):
            return self.detected_patterns_dict 
    
    def get_default_settings(self):
        return {"start_date": self.start_date, "end_date": self.end_date, "rsi_period": self.rsi_period, "interval":self.interval, "file_name" : self.file_name, "status":200}
    
    def update_user_input(self, json_data, file):

        try:
            interval = int(json_data['interval'])
            rsi_period = int(json_data['rsi_period'])
            stock_period = int(json_data['stock_period'])
            file = file['symbols_file']

            if interval < 10 or interval > 10000 or rsi_period < 1 or rsi_period > 99 or stock_period < 1 or stock_period > 10000:
                return jsonify({"message": "Please enter valid numbers", "status":400})
            
            if self.mime_type != file.content_type:
                return jsonify({"message": "Please choose a csv file", "status":400})
            
            self.interval = interval
            self.rsi_period = rsi_period
            self.stock_period = stock_period
            self.file_name = file.filename
            self.stock_file = file.readlines()

            self.end_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
            self.start_date = (datetime.now() - timedelta(days=self.stock_period)).strftime('%Y-%m-%d')

            return jsonify({"message": "Updated successfully", "status":200, "start_date": self.start_date, "end_date": self.end_date, "rsi_period": self.rsi_period, "interval":self.interval, "file_name" : self.file_name})
        except:
            return jsonify({"message": "Something went wrong...", "status":500})

pattern = PatternDetect()

@app.route('/get_default_settings')
def get_default_settings():
    return pattern.get_default_settings()

@app.route('/user_input', methods=['POST'])
def update_user_input():
    json_data = request.form
    file = request.files
    return pattern.update_user_input(json_data, file)

@app.route("/get_latest_data")
def get_latest_data():
   return pattern.get_stock_data()

@app.route("/run_interval_detection")
def run_interval_detection():
    pattern.run_interval_detection()
    result = {'message': 'Running...', "status":200}
    return jsonify(result)

@app.route("/symbols_file_example")
def stock_file_example():
    f = open('datasets/symbols.csv', 'r')
    content = f.readlines()
    f.close()
    return render_template("symbols_file_example.html", content=content)

@app.route("/")
def main():

    try:
        return render_template("index.html")
    except Exception as e:
        return "Oops, 500 Internal Server Error"
    

if __name__ == "__main__":
    app.run(debug=True, port="5000")
