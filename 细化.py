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

def execute_trade():
    while True:
        binance_symbol = symbol.replace('-', '')
        okx_symbol = symbol

        try:
            binance_price = get_binance_ticker_price(binance_symbol)
            okx_price = get_okx_ticker_price(okx_symbol)
        except Exception as e:
            print(f"Error fetching prices: {e}")
            continue

        if binance_price < okx_price:
            try:
                buy_order = place_binance_order(binance_symbol, 'BUY', trade_amount, binance_price)
                sell_order = place_okx_order(okx_symbol, 'sell', trade_amount, okx_price)
                trade_history.append({'timestamp': datetime.now(), 'buy': 'binance', 'sell': 'okx', 'price_diff': okx_price - binance_price})
            except Exception as e:
                print(f"Error placing orders: {e}")
        elif okx_price < binance_price:
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

