
import requests
import time
import hmac
import hashlib
import json

# OKX API配置
api_key = 'your_api_key'
secret_key = 'your_secret_key'
base_url = 'https://www.okx.com'

# 签名函数
def sign(params, secret_key):
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    sign_str = '&'.join([f'{x[0]}={x[1]}' for x in sorted_params])
    sign_str = sign_str + secret_key
    signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    return signature

# 获取账户余额
def get_account_balance():
    path = '/api/v5/account/balance'
    timestamp = str(int(time.time()))
    params = {'timestamp': timestamp}
    signature = sign(params, secret_key)

    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

    response = requests.get(base_url + path, headers=headers)
    return response.json()

# 下单函数
def place_order(symbol, side, price, size, leverage):
    path = '/api/v5/trade/order'
    timestamp = str(int(time.time()))

    params = {
        'instId': symbol,
        'tdMode': 'cross',
        'side': side,
        'ordType': 'limit',
        'px': price,
        'sz': size,
        'lever': leverage,
        'timestamp': timestamp
    }

    signature = sign(params, secret_key)

    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

    response = requests.post(base_url + path, headers=headers, data=json.dumps(params))
    return response.json()

# 策略示例：动量突破 + 反转交易
def strategy():
    # 获取账户余额
    balance = get_account_balance()
    # TODO: 根据您的需求解析余额数据

    # 获取市场数据
    # TODO: 使用OKX API获取市场数据，计算策略所需指标

    # 确定交易信号
    # TODO: 根据策略计算交易信号

    # 下单
    # TODO: 根据交易信号调用place_order()函数进行交易

if __name__ == '__main__':
    strategy()
