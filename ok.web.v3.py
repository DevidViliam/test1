

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


# 省略之前的代码，与上文相同

# 设置止损止盈价格
def calculate_stop_loss_take_profit(entry_price, stop_loss_percentage, take_profit_percentage):
    stop_loss_price = entry_price * (1 - stop_loss_percentage)
    take_profit_price = entry_price * (1 + take_profit_percentage)
    return stop_loss_price, take_profit_price

# 计算仓位大小
def calculate_position_size(account_balance, risk_percentage):
    position_size = account_balance * risk_percentage
    return position_size

# 下单函数（修改）
def place_order(symbol, side, price, size, leverage, stop_loss_price, take_profit_price):
    # 省略之前的代码，与上文相同

    # 添加止损止盈参数
    params.update({
        'slPx': stop_loss_price,
        'tpPx': take_profit_price
    })

    # 省略之前的代码，与上文相同

# 策略示例：动量突破（修改）
def strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage):
    # 省略之前的代码，与上文相同

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


=============
在此版本的量化程序中，我们将引入多个技术指标，如移动平均线（MA）、相对强弱指数（RSI），以及对冲策略来进一步提升策略效果。以下是程序的修改部分：
在此版本的量化程序中，我们引入了移动平均线和相对强弱指数作为交易信号的判断依据，同时调整了generate_signal函数。这将有助于进一步提升策略效果。

此外，您还可以考虑引入对冲策略，以降低市场风险。例如，在执行多头交易时，可以同时在其他品种或市场上执行空头交易，以抵消市场波动带来的影响。

请注意，投资有风险，操作需谨慎。在实际应用中，建议进行充分的研究和测试，以确保策略的有效性和可行性。在使用高杠杆合约时，要特别关注风险管理，以避


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

# 判断交易信号（修改）
def generate_signal(data):
    last_row = data.iloc[-1]
    if last_row['momentum'] > 0 and last_row['rsi'] < 30 and last_row['close'] > last_row['ma10']:
        return 'buy'
    elif last_row['momentum'] < 0 and last_row['rsi'] > 70 and last_row['close'] < last_row['ma10']:
        return 'sell'
    else:
        return 'hold'

# 策略示例：动量突破（修改）
def strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage):
    # 省略之前的代码，与上文相同

    # 计算移动平均线
    df = calculate_moving_average(df, 10)

    # 计算相对强弱指数
    df = calculate_rsi(df)

    # 判断交易信号
    signal = generate_signal(df)

# 省略之前的代码，与上文相同



AIM:

为了进一步完善量化程序，我们可以考虑添加市场情绪分析和多策略组合，这将有助于提高策略的稳定性和收益潜力。

市场情绪分析：分析市场上的新闻、社交媒体等信息，以评估市场情绪。市场情绪分析可以帮助我们捕捉市场的短期波动，从而改善交易策略。

多策略组合：通过组合多个独立的交易策略，可以提高策略的稳定性，降低单一策略带来的风险。例如，可以将基于技术分析、基本面分析和市场情绪分析的策略组合在一起，以提高整体的收益潜力。

这里我们将简要演示如何添加市场情绪分析和多策略组合：

import requests
from sentiment_analysis import analyze_sentiment

# 市场情绪分析
def get_market_sentiment(symbol):
    # TODO: 获取与交易品种相关的新闻或社交媒体信息
    news = requests.get(f'https://api.example.com/news?symbol={symbol}')
    sentiment_score = analyze_sentiment(news.text)
    return sentiment_score

# 多策略组合
def multi_strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage):
    # 获取市场情绪
    sentiment_score = get_market_sentiment(symbol)

    # 确定策略权重
    momentum_strategy_weight = 0.4
    sentiment_strategy_weight = 0.6

    # 执行策略
    if sentiment_score > 0.5:
        strategy(symbol, interval, stop_loss_percentage, take_profit_percentage, risk_percentage, weight=momentum_strategy_weight)
    else:
        # TODO: 添加其他策略并执行
        pass

在此版本的量化程序中，我们引入了市场情绪分析和多策略组合。这将有助于提高策略的稳定性和收益潜力。

请注意，投资有风险，操作需谨慎。在实际应用中，建议进行充分的研究和测试，以确保策略的有效性和可行性。在使用高杠杆合约时，要特别关注风险管理，以避免可能的重大损失。

为了进一步提高策略的灵活性和实时性，我们可以添加自适应参数优化和实时监控功能。以下是如何实现这些功能的示例：

#自适应参数优化：使用遗传算法、网格搜索等方法，对策略参数进行实时优化，以适应市场变化。

from evolutionary_algorithm import optimize_parameters

def adaptive_parameters_optimization(symbol, interval, initial_parameters):
    # 根据市场数据，使用遗传算法优化策略参数
    best_parameters = optimize_parameters(symbol, interval, initial_parameters)
    return best_parameters

# 在策略执行时，添加自适应参数优化
adaptive_params = adaptive_parameters_optimization(symbol, interval, initial_parameters)
strategy(symbol, interval, *adaptive_params)

#实时监控功能：实时监控市场数据、交易信号和仓位变化，根据市场情况及时调整策略。
import threading

def realtime_monitoring(symbol, interval, params):
    while True:
        # 获取实时市场数据
        market_data = get_market_data(symbol, interval)

        # 分析市场数据，生成交易信号
        signal = generate_signal(market_data, params)

        # 根据交易信号调整策略
        adjust_strategy(signal, params)

        # 等待下一个时间间隔
        time.sleep(interval)

# 在策略执行时，启动实时监控功能
monitoring_thread = threading.Thread(target=realtime_monitoring, args=(symbol, interval, adaptive_params))
monitoring_thread.start()

#在此版本的量化程序中，我们引入了自适应参数优化和实时监控功能。这将有助于提高策略的灵活性和实时性。


#模型评估与回测：通过历史数据对策略进行回测，分析策略在不同市场环境下的表现，以评估策略的稳定性和可靠性。

import backtrader as bt

class MyStrategy(bt.Strategy):
    # TODO: 在此处定义策略逻辑

def backtest_strategy(strategy, data, params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy, *params)

    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)

    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    initial_portfolio_value = cerebro.broker.getvalue()
    cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()

    return initial_portfolio_value, final_portfolio_value

# 通过回测评估策略
historical_data = get_historical_data(symbol, interval)
initial_value, final_value = backtest_strategy(MyStrategy, historical_data, adaptive_params)



#性能指标：计算策略的各种性能指标，如夏普比率、最大回撤、盈亏比等，以衡量策略的风险和收益潜力。
from performance_metrics import calculate_performance_metrics

def evaluate_strategy(initial_value, final_value, data, trades):
    performance_metrics = calculate_performance_metrics(initial_value, final_value, data, trades)
    return performance_metrics

# 计算性能指标
performance_metrics = evaluate_strategy(initial_value, final_value, historical_data, trades)



=========================
#仓位管理：根据市场波动性和风险承受能力动态调整仓位大小。

def position_sizing(symbol, interval, risk_percentage, account_value):
    # 计算市场波动性
    volatility = calculate_volatility(symbol, interval)

    # 根据风险百分比和账户价值计算仓位大小
    position_size = account_value * risk_percentage / volatility
    return position_size

position_size = position_sizing(symbol, interval, risk_percentage, account_value)

#止损与止盈：设定止损与止盈水平，以控制单笔交易的风险。

def set_stop_loss_take_profit(symbol, entry_price, stop_loss_percentage, take_profit_percentage):
    stop_loss_level = entry_price * (1 - stop_loss_percentage)
    take_profit_level = entry_price * (1 + take_profit_percentage)
    return stop_loss_level, take_profit_level

stop_loss_level, take_profit_level = set_stop_loss_take_profit(symbol, entry_price, stop_loss_percentage, take_profit_percentage)


#风险平衡：在多策略组合中，对各策略的权重进行风险平衡，以降低整体策略的风险。
def risk_balancing(strategy_weights, strategy_risks):
    adjusted_weights = {}

    for strategy, weight in strategy_weights.items():
        adjusted_weights[strategy] = weight / strategy_risks[strategy]

    total_weight = sum(adjusted_weights.values())
    for strategy in adjusted_weights:
        adjusted_weights[strategy] /= total_weight

    return adjusted_weights

adjusted_weights = risk_balancing(strategy_weights, strategy_risks)

