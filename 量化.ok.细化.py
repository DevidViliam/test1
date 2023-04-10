import requests
import json
import hmac
import hashlib
import time
from threading import Thread

# Binance API
binance_api_key = '1111111111111111'
binance_secret_key = 'your_binance_secret_key'

# OKX API
okx_api_key = '1111111111111111'
okx_secret_key = 'your_okx_secret_key'
okx_passphrase = 'your_passphrase'

# Parameters
symbol = 'BTCUSDT'
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

def execute_trade():
    while True:
        binance_price = get_binance_ticker_price(symbol)
        okx_price = get_okx_ticker_price(symbol)

        if binance_price < okx_price:
            # Buy on Binance, sell on OKX
            print(f"Buy on Binance at {binance_price}, sell on OKX at {okx_price}")
            # Place your buy and sell orders using the respective APIs
        elif okx_price < binance_price:
            # Buy on OKX, sell on Binance
            print(f"Buy on OKX at {okx_price}, sell on Binance at {binance_price}")
            # Place your buy and sell orders using the respective APIs

        time.sleep(1)

# Main Function
def main():
    trading_thread = Thread(target=execute_trade

