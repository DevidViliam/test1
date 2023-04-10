
import requests
import time
import hmac
import hashlib
import json
import pandas as pd
import numpy as np

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

# 获取K线数据
def get_kline_data(symbol, interval):
    path = f'/api/v5/market/candles'
    params = {
        'instId': symbol,
        'after': int(time.time()) - interval * 200,
        'before': int(time.time()),
        'bar': f'{interval}s',
        'limit': 200
    }
    response = requests.get(base_url + path, params=params)
    return response.json()

# 计算动量指标
def calculate_momentum(data, period=14):
    data['momentum'] = data['close'].diff(period)
    return data

# 判断交易信号
def generate_signal(data):
    last_row = data.iloc[-1]
    if last_row['momentum'] > 0:
        return 'buy'
    elif last_row['momentum'] < 0:
        return 'sell'
    else:
        return 'hold'

# 下单函数
def place_order(symbol, side, price, size, leverage):
    # 省略之前的代码，与上文相同

# 策略示例：动量突破
def strategy(symbol, interval):
    # 获取K线数据
    kline_data = get_kline_data(symbol, interval)

    # 处理K线数据
    df = pd.DataFrame(kline_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'currency_volume'])
    df[['open', 'high', 'low', 'close', 'volume', 'currency_volume']] = df[['open', 'high', 'low', 'close', 'volume', 'currency_volume']].apply(pd.to_numeric)

    # 计算动量指标
    df = calculate_momentum(df)

    # 判断交易信号
    signal = generate_signal(df)

    # 下单
    if signal == 'buy':
        # 根据您的需求调整下单参数
        place_order(symbol, 'buy', df.iloc[-1]['close'], 1, 10)
    elif signal == 'sell':
        # 根据您的需求调整下单参数
        place_order(symbol, 'sell', df.iloc[-1]['close'], 1, 10)

if name == 'main':
# 设定交易品种和时间间隔
symbol = 'BTC-USDT'
interval = 60

while True:
    try:
        strategy(symbol, interval)
        print(f"Executed strategy at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
        time.sleep(interval)
    except Exception as e:
        print(f"Error executing strategy: {str(e)}")
        time.sleep(5)

