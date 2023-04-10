

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
    if last_row['momentum'] > 0 and last_row['rsi'] < 30 and last_row['close'] > last_row['ma10']:
        return 'buy'
    elif last_row['momentum'] < 0 and last_row['rsi'] > 70 and last_row['close'] < last_row['ma10']:
        return 'sell'
    else:
        return 'hold'

# 设置止损止盈价格
def calculate_stop_loss_take_profit(entry_price, stop_loss_percentage, take_profit_percentage):
    stop_loss_price = entry_price * (1 - stop_loss_percentage)
    take_profit_price = entry_price * (1 + take_profit_percentage)
    return stop_loss_price, take_profit_price

# 计算仓位大小
def calculate_position_size(account_balance, risk_percentage):
    position_size = account_balance * risk_percentage
    return position_size
    
# 下单函数
def place_order(symbol, side, price, size, leverage, stop_loss_price, take_profit_price):
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
    
    # 添加止损止盈参数
    params.update({
        'slPx': stop_loss_price,
        'tpPx': take_profit_price
    })

    signature = sign(params, secret_key)

    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

    response = requests.post(base_url + path, headers=headers, data=json.dumps(params))
    return response.json()

# 策略示例：动量突破
def strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage):
    # 获取K线数据
    kline_data = get_kline_data(symbol, interval)

    # 处理K线数据
    df = pd.DataFrame(kline_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'currency_volume'])
    df[['open', 'high', 'low', 'close', 'volume', 'currency_volume']] = df[['open', 'high', 'low', 'close', 'volume', 'currency_volume']].apply(pd.to_numeric)

    # 计算动量指标
    df = calculate_momentum(df)
    
    # 计算移动平均线
    df = calculate_moving_average(df, 10)

    # 计算相对强弱指数
    df = calculate_rsi(df)

    # 判断交易信号
    signal = generate_signal(df)

    # 获取账户余额
    balance = get_account_balance()
    # TODO: 根据您的需求解析余额数据，获取账户总资金

    # 计算仓位大小
    position_size = calculate_position_size(account_balance, risk_percentage)

    # 下单
    if signal == 'buy':
        entry_price = df.iloc[-1]['close']
        stop_loss_price, take_profit_price = calculate_stop_loss_take_profit(entry_price, stop_loss_percentage, take_profit_percentage)
        place_order(symbol, 'buy', entry_price, position_size, 10, stop_loss_price, take_profit_price)
    elif signal == 'sell':
        entry_price = df.iloc[-1]['close']
        stop_loss_price, take_profit_price = calculate_stop_loss_take_profit(entry_price, stop_loss_percentage, take_profit_percentage)
        place_order(symbol, 'sell', entry_price, position_size, 10, stop_loss_price, take_profit_price)

# 计算移动平均线
def calculate_moving_average(data, period):
    data[f'ma{period}'] = data['close'].rolling(window=period).mean()
    return data

# 计算相对强弱指数
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain, loss = delta.copy(), delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = -loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    data['rsi'] = 100 - (100 / (1 + rs))
    return data
    
if __name__ == '__main__':
    # 设定交易品种、时间间隔和策略参数
    symbol = 'BTC-USDT'
    interval = 60
    stop_loss_percentage = 0.01
    take_profit_percentage = 0.02
    risk_percentage = 0.02

while True:
    try:
        strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage)
        print(f"Executed strategy at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
        time.sleep(interval)
    except Exception as e:
        print(f"Error executing strategy: {str(e)}")
        time.sleep(5)
