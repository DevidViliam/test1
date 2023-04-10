import requests
import json
import hmac
import hashlib
import time
from threading import Thread
from collections import deque
from datetime import datetime

# Binance API
binance_api_key = '1111111111111111'
binance_secret_key = 'your_binance_secret_key'

# OKX API
okx_api_key = '1111111111111111'
okx_secret_key = 'your_okx_secret_key'
okx_passphrase = 'your_passphrase'

# Parameters
symbol = 'BTC-USDT'
trade_amount = 0.001

# Binance API Functions
def binance_request(method, endpoint, api_key, secret_key, params=None):
    url = f'https://api.binance.com{endpoint}'
    headers = {'X-MBX-APIKEY': api_key}
    
    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=params)
    
    return json.loads(response.text)

# OKX API Functions
def okx_request(method, endpoint, api_key, secret_key, params=None):
    url = f'https://www.okx.com{endpoint}'
    headers = {'OK-ACCESS-KEY': api_key,
               'OK-ACCESS-SIGN': generate_okx_signature(method, endpoint, params, secret_key),
               'OK-ACCESS-TIMESTAMP': str(time.time()),
               'OK-ACCESS-PASSPHRASE': okx_passphrase}
    
    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=params)
    
    return json.loads(response.text)

def generate_okx_signature(method, endpoint, params, secret_key):
    timestamp = str(time.time())
    pre_hash = timestamp + method.upper() + endpoint + (json.dumps(params) if params else '')
    signature = hmac.new(bytes(secret_key, 'utf-8'), bytes(pre_hash, 'utf-8'), hashlib.sha256)
    return signature.hexdigest()

# Strategy Functions
def get_binance_ticker_price(symbol):
    params = {'symbol': symbol}
    response = binance_request('GET', '/api/v3/ticker/price', binance_api_key, binance_secret_key, params)
    return float(response['price'])

def get_okx_ticker_price(symbol):
    response = okx_request('GET', f'/api/v5/market/ticker/{symbol}', okx_api_key, okx_secret_key)
    return float(response[0]['askPx'])

# Trading Functions
def place_binance_order(symbol, side, quantity, price):
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': price
    }
    return binance_request('POST', '/api/v3/order', binance_api_key, binance_secret_key, params)

def place_okx_order(symbol, side, size, price):
    params = {
        'instId': symbol,
        'tdMode': 'cash',
        'side': side.upper(),
        'ordType': 'limit',
        'sz': size,
        'px': price
    }
    return okx_request('POST', '/api/v5/trade/order', okx_api_key, okx_secret_key, params)

# ... (previous code remains the same, including import statements, API functions, and trading functions)

# Trade tracking
trade_history = deque(maxlen=100)

# Rate limiting
binance_rate_limit = 1200
okx_rate_limit = 300
last_binance_request = time.time()
last_okx_request = time.time()

def rate_limited_request(exchange, method, endpoint, api_key, secret_key, params=None):
    global last_binance_request, last_okx_request

    if exchange == 'binance':
        while time.time() - last_binance_request < 1 / (binance_rate_limit / 60):
            time.sleep(0.05)
        last_binance_request = time.time()
        return binance_request(method, endpoint, api_key, secret_key, params)
    elif exchange == 'okx':
        while time.time() - last_okx_request < 1 / (okx_rate_limit / 60):
            time.sleep(0.05)
        last_okx_request = time.time()
        return okx_request(method, endpoint, api_key, secret_key, params)

# ... (previous code remains the same, including import statements, API functions, and trading functions)

# Strategy optimization
def calculate_sma(data, window):
    return sum(data[-window:]) / window

def get_binance_historical_klines(symbol, interval, limit):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    return rate_limited_request('binance', 'GET', '/api/v3/klines', binance_api_key, binance_secret_key, params)

def get_okx_historical_klines(symbol, interval, limit):
    params = {'instId': symbol, 'bar': interval, 'limit': limit}
    return rate_limited_request('okx', 'GET', '/api/v5/market/candles', okx_api_key, okx_secret_key, params)

def generate_trade_signal(short_term_window, long_term_window):
    binance_symbol = symbol.replace('-', '')
    okx_symbol = symbol

    binance_klines = get_binance_historical_klines(binance_symbol, '1h', long_term_window)
    okx_klines = get_okx_historical_klines(okx_symbol, '1H', long_term_window)

    binance_closing_prices = [float(kline[4]) for kline in binance_klines]
    okx_closing_prices = [float(kline[4]) for kline in okx_klines]

    binance_short_sma = calculate_sma(binance_closing_prices, short_term_window)
    binance_long_sma = calculate_sma(binance_closing_prices, long_term_window)
    okx_short_sma = calculate_sma(okx_closing_prices, short_term_window)
    okx_long_sma = calculate_sma(okx_closing_prices, long_term_window)

    binance_signal = binance_short_sma > binance_long_sma
    okx_signal = okx_short_sma > okx_long_sma

    return binance_signal, okx_signal

# ... (rest of the code remains the same, including rate_limited_request function and execute_trade function)

def execute_trade():
    short_term_window = 5
    long_term_window = 20

    while True:
        try:
            binance_signal, okx_signal = generate_trade_signal(short_term_window, long_term_window)
        except Exception as e:
            print(f"Error generating trade signals: {e}")
            continue

        binance_symbol = symbol.replace('-', '')
        okx_symbol = symbol

        try:
            binance_price = get_binance_ticker_price(binance_symbol)
            okx_price = get_okx_ticker_price(okx_symbol)
        except Exception as e:
            print(f"Error fetching prices: {e}")
            continue

        if binance_signal and not okx_signal:
            # Buy on Binance, sell on OKX
            try:
                buy_order = place_binance_order(binance_symbol, 'BUY', trade_amount, binance_price)
                sell_order = place_okx_order(okx_symbol, 'sell', trade_amount, okx_price)
                trade_history.append({'timestamp': datetime.now(), 'buy': 'binance', 'sell': 'okx', 'price_diff': okx_price - binance_price})
            except Exception as e:
                print(f"Error placing orders: {e}")

        elif okx_signal and not binance_signal:
            # Buy on OKX, sell on Binance
            try:
                buy_order = place_okx_order(okx_symbol, 'buy', trade_amount, okx_price)
                sell_order = place_binance_order(binance_symbol, 'SELL', trade_amount, binance_price)
                trade_history.append({'timestamp': datetime.now(), 'buy': 'okx', 'sell': 'binance', 'price_diff': binance_price - okx_price})
            except Exception as e:
                print(f"Error placing orders: {e}")

        print(f"Trade history (last 5): {list(trade_history)[-5:]}")
        time.sleep(1)

# Main Function
def main():
    trading_thread = Thread(target=execute_trade)
    trading_thread.start()

if __name__ == '__main__':
    main()


#Exponential Moving Averages (EMA):
def calculate_ema(data, window, prev_ema=None):
    multiplier = 2 / (window + 1)
    if prev_ema is None:
        return calculate_sma(data[-window:], window)
    return (data[-1] - prev_ema) * multiplier + prev_ema

#Moving Average Convergence Divergence (MACD):
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = [calculate_ema(data[:i+1], short_window) for i in range(len(data))]
    long_ema = [calculate_ema(data[:i+1], long_window) for i in range(len(data))]
    macd_line = [short - long for short, long in zip(short_ema, long_ema)]
    signal_line = [calculate_ema(macd_line[:i+1], signal_window) for i in range(len(macd_line))]
    return macd_line, signal_line

#Relative Strength Index (RSI):
def calculate_rsi(data, window=14):
    gains, losses = [], []
    for i in range(1, len(data)):
        change = data[i] - data[i - 1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = [sum(gains[:window]) / window] + [0] * (len(gains) - window)
    avg_loss = [sum(losses[:window]) / window] + [0] * (len(losses) - window)

    for i in range(window, len(gains)):
        avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gains[i]) / window
        avg_loss[i] = (avg_loss[i - 1] * (window - 1) + losses[i]) / window

    rs = [gain / loss if loss != 0 else 0 for gain, loss in zip(avg_gain, avg_loss)]
    rsi = [100 - (100 / (1 + r)) for r in rs]

    return rsi

#Bollinger Bands:
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    sma = [calculate_sma(data[:i+1], window) for i in range(len(data))]
    std_dev = [np.std(data[max(0, i-window+1):i+1]) for i in range(len(data))]
    upper_band = [mean + num_std_dev * std for mean, std in zip(sma, std_dev)]
    lower_band = [mean - num_std_dev * std for mean, std in zip(sma, std_dev)]

    return sma, upper_band, lower_band

#Machine Learning and Artificial Intelligence:
#Implementing machine learning algorithms in a trading strategy requires a more in-depth approach, but here's a simple example using a linear regression model to predict future price movements:
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def train_linear_regression_model(prices, window=30):
    X, y = [], []
    for i in range(window, len(prices)):
        X.append(prices[i-window:i])
        y.append(prices[i])
    X, y = np.array(X), np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    return model, score

#Sentiment Analysis:
#Incorporating sentiment analysis would involve fetching and analyzing news articles or social media posts. Here's a basic example using the TextBlob library for sentiment analysis:
from textblob import TextBlob

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

#Portfolio Optimization:
#Here's an example of portfolio optimization using Modern Portfolio Theory (MPT) and the Efficient Frontier with the PyPortfolioOpt library:
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

def optimize_portfolio(prices):
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    return cleaned_weights

#Stop Loss and Take Profit Orders:
def place_stop_loss_order(price, stop_loss_pct):
    return price * (1 - stop_loss_pct)

def place_take_profit_order(price, take_profit_pct):
    return price * (1 + take_profit_pct)

#Time-based Strategies:
from datetime import time

def is_european_session(timestamp):
    session_start, session_end = time(7, 0), time(16, 0)
    return session_start <= timestamp.time() <= session_end

#Trading Volume Analysis (On-Balance Volume):
def calculate_obv(prices, volumes):
    obv = [volumes[0] if prices[0] > prices[-1] else -volumes[0]]
    for i in range(1, len(prices)):
        volume = volumes[i]
        if prices[i] > prices[i - 1]:
            obv.append(obv[-1] + volume)
        elif prices[i] < prices[i - 1]:
            obv.append(obv[-1] - volume)
        else:
            obv.append(obv[-1])
    return obv

#Risk Management (Position Sizing):
#In this example, we use the percentage of equity risk model for position sizing.
def calculate_position_size(account_equity, risk_pct, entry_price, stop_loss_price):
    risk_amount = account_equity * risk_pct
    position_size = risk_amount / abs(entry_price - stop_loss_price)
    return position_size

#Adaptive Moving Averages:
def calculate_kama(prices, window=10, smoothing_constant=2):
    er_period = 10
    fast_length = 2
    slow_length = 30
    fast_constant = 2 / (fast_length + 1)
    slow_constant = 2 / (slow_length + 1)

    er_list = []
    for i in range(er_period, len(prices)):
        er = abs(prices[i] - prices[i - er_period]) / sum([abs(prices[i] - prices[i - 1]) for i in range(i - er_period + 1, i + 1)])
        er_list.append(er)

    kama_list = [sum(prices[:window]) / window] * window
    for i in range(window, len(prices)):
        sc = (er_list[i - window] * (fast_constant - slow_constant) + slow_constant) ** 2
        kama = kama_list[-1] + sc * (prices[i] - kama_list[-1])
        kama_list.append(kama)

    return kama_list

#ATR-based Stop Loss:
def calculate_atr(highs, lows, closes, window=14):
    tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(1, len(highs))]
    atr = [sum(tr[:window]) / window] * window
    for i in range(window, len(tr)):
        atr.append((atr[-1] * (window - 1) + tr[i]) / window)
    return atr

def place_atr_stop_loss(entry_price, atr, atr_multiplier):
    return entry_price - atr * atr_multiplier

#Portfolio Rebalancing:
def rebalance_portfolio(portfolio, target_allocation):
    current_allocation = {asset: (value / sum(portfolio.values())) for asset, value in portfolio.items()}
    orders = {}

    for asset in portfolio:
        difference = target_allocation[asset] - current_allocation[asset]
        if difference > 0:
            orders[asset] = ('buy', difference)
        elif difference < 0:
            orders[asset] = ('sell', -difference)
    return orders

#a. Fixed Percentage Stop Loss:
def fixed_percentage_stop_loss(entry_price, stop_loss_pct):
    stop_loss_price = entry_price * (1 - stop_loss_pct)
    return stop_loss_price

#b. ATR Stop Loss:
def atr_stop_loss(entry_price, atr, atr_multiplier):
    stop_loss_price = entry_price - (atr * atr_multiplier)
    return stop_loss_price

#c. Trailing Stop Loss:
def trailing_stop_loss(highest_price_since_entry, trailing_stop_distance):
    stop_loss_price = highest_price_since_entry - trailing_stop_distance
    return stop_loss_price

#a. Fixed Dollar Amount:
def fixed_dollar_amount_position_size(dollar_amount, asset_price):
    position_size = dollar_amount / asset_price
    return position_size

#b. Percentage of Account Equity:
def percentage_of_account_equity_position_size(account_equity, allocation_pct, asset_price):
    position_size = (account_equity * allocation_pct) / asset_price
    return position_size

#c. Risk-Based Position Sizing:
def risk_based_position_size(account_equity, risk_pct, entry_price, stop_loss_price):
    risk_amount = account_equity * risk_pct
    position_size = risk_amount / abs(entry_price - stop_loss_price)
    return position_size

#Portfolio diversification:
#For this example, let's assume you have a list of assets and their target allocations. The following function can help you rebalance your portfolio to match the target allocations:
def rebalance_portfolio(current_holdings, target_allocations):
    rebalance_orders = {}
    total_value = sum(current_holdings.values())
    for asset, current_value in current_holdings.items():
        target_value = total_value * target_allocations[asset]
        if current_value < target_value:
            rebalance_orders[asset] = ("buy", target_value - current_value)
        elif current_value > target_value:
            rebalance_orders[asset] = ("sell", current_value - target_value)
    return rebalance_orders

#Maximum Drawdown:
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

#Value at Risk (VaR):
import numpy as np

def calculate_var(returns, confidence_level=0.95):
    returns_sorted = np.sort(returns)
    index = int((1 - confidence_level) * len(returns_sorted))
    var = -returns_sorted[index]
    return var

#Conditional Value at Risk (CVaR):
def calculate_cvar(returns, confidence_level=0.95):
    returns_sorted = np.sort(returns)
    index = int((1 - confidence_level) * len(returns_sorted))
    cvar = -np.mean(returns_sorted[:index])
    return cvar

#Portfolio Correlation:
import pandas as pd

def calculate_portfolio_correlation(asset_returns):
    correlation_matrix = asset_returns.corr()
    return correlation_matrix






#Stop-loss orders:
def place_fixed_percentage_stop_loss(entry_price, percentage):
    stop_loss_price = entry_price * (1 - percentage)
    return stop_loss_price

def update_trailing_stop_loss(highest_price_since_entry, trailing_stop_distance):
    stop_loss_price = highest_price_since_entry - trailing_stop_distance
    return stop_loss_price

#Position sizing:头寸规模
def fixed_dollar_amount_position_size(account_equity, dollar_amount, asset_price):
    position_size = dollar_amount / asset_price
    return position_size

def percentage_of_equity_position_size(account_equity, percentage, asset_price):
    position_size = (account_equity * percentage) / asset_price
    return position_size


#Portfolio diversification: 投资组合多元化
def calculate_portfolio_weights(asset_returns, risk_tolerance):
    covariance_matrix = asset_returns.cov()
    inverse_covariance_matrix = np.linalg.inv(covariance_matrix)
    ones = np.ones(len(asset_returns.columns))
    weights = np.dot(inverse_covariance_matrix, ones) / np.dot(np.dot(ones, inverse_covariance_matrix), ones)
    return pd.Series(weights, index=asset_returns.columns)

def rebalance_portfolio(current_holdings, target_allocations):
    rebalance_orders = {}
    total_value = sum(current_holdings.values())
    for asset, current_value in current_holdings.items():
        target_value = total_value * target_allocations[asset]
        if current_value < target_value:
            rebalance_orders[asset] = ("buy", target_value - current_value)
        elif current_value > target_value:
            rebalance_orders[asset] = ("sell", current_value - target_value)
    return rebalance_orders


#必须pip install ccxt

import ccxt
import time

# Initialize the ccxt library with the chosen exchange
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret',
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
timeframe = '1m'

# Get real-time ticker information
def get_ticker():
    ticker = exchange.fetch_ticker(symbol)
    return ticker

# Get real-time order book depth
def get_order_book(depth=10):
    order_book = exchange.fetch_order_book(symbol, limit=depth)
    return order_book

# Example trading decision function using real-time data
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

while True:
    try:
        make_trading_decision()
        time.sleep(60)  # Run the decision-making process every minute
    except Exception as e:
        print(e)
        time.sleep(60)


#Sharpe Ratio:
import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe_ratio

#Maximum Drawdown:
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

#Return on Investment (ROI):
def calculate_roi(initial_investment, final_value):
    roi = (final_value - initial_investment) / initial_investment
    return roi

