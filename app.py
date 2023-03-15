from flask import Flask, render_template, jsonify
import talib
import yfinance as yf
import pandas
from patterns import candlestick_patterns
from dataclasses import dataclass
import datetime
import os

app = Flask(__name__)

@app.route('/generate_csv')
def generate_stock_csv():

    with open('datasets/symbols.csv', 'r') as file:
        
        for line in file:
            if "," not in line:
                continue
            symbol = line.split(",")[0]
            data = yf.download(symbol, start="2023-01-01", end="2023-3-15")
            data.to_csv('datasets/daily/{}.csv'.format(symbol))

    result = {
        'message': 'Stock CSVs Generated'
    }
    return jsonify(result)


@dataclass
class RSI:

    symbol: str = "SPY"
    time_period: int = 14 
    start_time: datetime = datetime.time(hour=7)
    end_time: datetime = datetime.time(hour=13)

    def compute_RSI(self):
        current_time = datetime.datetime.now().time()

        if current_time >= self.start_time and current_time <= self.end_time:
            data = yf.download(self.symbol, period="1d", interval="1m")
            rsi = talib.RSI(data['Close'], timeperiod=self.time_period)[-1]
            print("Current RSI:", rsi)
            return rsi
        else:
            print("Markets Closed...")
            return -1


@app.route("/patterns")
def detect_patterns():
    detected_patterns_dict = {}
    rsi = RSI()

    for filename in os.listdir('datasets/daily'):

        df = pandas.read_csv('datasets/daily/{}'.format(filename))
        stock = filename
        rsi = RSI(symbol=filename).compute_RSI()
        computed_rsi = f"RSI: {rsi}"

        for sym, pat in candlestick_patterns.items():

            dynamic_pattern_call = getattr(talib, sym)

            try:
                results = dynamic_pattern_call(df['Open'], df['High'], df['Low'], df['Close'])
                last = results.tail(1).values[0]
                if last > 0:
                    detected_patterns_dict[stock] = ['bullish', pat, computed_rsi]
                    break
                elif last < 0:
                    detected_patterns_dict[stock] = ['bearish', pat, computed_rsi]
                    break
                else:
                    detected_patterns_dict[stock] = ['neutral', "no patterns detected", computed_rsi]
            except Exception as e:
                print('failed on filename: {}'.format(filename))

    return detected_patterns_dict

@app.route("/")
def main():

    try:
        detected_patterns = detect_patterns()
        return render_template("index.html", detected_patterns=detected_patterns)
    except:
        return "Oops 500 Internal Server Error"
    

if __name__ == "__main__":
    app.run(debug=True, port="5000")
