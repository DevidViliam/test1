import ccxt
import time
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
import threading

# Initialize the ccxt library with the chosen exchange
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret',
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
timeframe = '1m'
app = Flask(__name__)

def get_ticker():
    ticker = exchange.fetch_ticker(symbol)
    return ticker

def get_order_book(depth=10):
    order_book = exchange.fetch_order_book(symbol, limit=depth)
    return order_book

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe_ratio

def calculate_maximum_drawdown(returns):
    cumulative_returns = [1 + r for r in returns]
    for i in range(1, len(cumulative_returns)):
        cumulative_returns[i] *= cumulative_returns[i - 1]

    max_drawdown = 0
    peak_value = cumulative_returns[0]

    for i in range(1, len(cumulative_returns)):
        if cumulative_returns[i] > peak_value:
            peak_value = cumulative_returns[i]
        else:
            drawdown = (peak_value - cumulative_returns[i]) / peak_value
            max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown

def calculate_roi(initial_investment, final_value):
    roi = (final_value - initial_investment) / initial_investment
    return roi

def start_trading():
    global is_trading
    is_trading = True

    while is_trading:
        try:
            make_trading_decision()
            time.sleep(60)  # Run the decision-making process every minute
        except Exception as e:
            print(e)
            time.sleep(60)

def stop_trading():
    global is_trading
    is_trading = False

def make_trading_decision():
    ticker = get_ticker()
    order_book = get_order_book()

    bid_price = order_book['bids'][0][0]
    ask_price = order_book['asks'][0][0]

    # Implement your trading logic here using real-time data
    # This is just a simple example that doesn't take into account other factors like position sizing, risk management, etc.
    if ask_price < ticker['close'] * 0.99:
        print("Buy signal")
    elif bid_price > ticker['close'] * 1.01:
        print("Sell signal")
    else:
        print("No action")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def web_start_trading():
    thread = threading.Thread(target=start_trading)
    thread.start()
    return "Trading started."

@app.route('/stop', methods=['POST'])
def web_stop_trading():
    stop_trading()
    return "Trading stopped."

if __name__ == '__main__':
    app.run(debug=True)


