
import pandas as pd
import numpy as np

# 均线交易策略
def moving_average_strategy(data, short_window=5, long_window=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# 动量交易策略
def momentum_strategy(data, n=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['momentum'] = data['close'].pct_change(periods=n)
    signals['signal'][n:] = np.where(signals['momentum'][n:] > 0, 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# 日内交易策略
def intraday_strategy(data, hour_start=10, hour_end=14):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['signal'][(data.index.hour >= hour_start) & (data.index.hour <= hour_end)] = 1.0
    signals['positions'] = signals['signal'].diff()
    return signals

# 突破交易策略
def breakout_strategy(data, n=20):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['high'] = data['high'].rolling(window=n, min_periods=1, center=False).max()
    signals['low'] = data['low'].rolling(window=n, min_periods=1, center=False).min()
    signals['signal'] = np.where(data['close'] > signals['high'], 1.0, np.where(data['close'] < signals['low'], -1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

# 反转交易策略
def reversal_strategy(data, n=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['returns'] = np.log(data['close'] / data['close'].shift(1))
    signals['signal'] = np.where(signals['returns'] < signals['returns'].rolling(window=n, min_periods=1, center=False).mean(), 1.0, -1.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# 调用策略函数
signals_ma = moving_average_strategy(data)
signals_momentum = momentum_strategy(data)
signals_intraday = intraday_strategy(data)
signals_breakout = breakout_strategy(data)
signals_reversal = reversal_strategy(data)

# 组合策略
signals = pd.DataFrame(index=data.index)
signals['signal'] = signals_ma['signal'] + signals




import pandas as pd
import numpy as np

# 均线交易策略
def moving_average_strategy(data, short_window=5, long_window=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# 动量交易策略
def momentum_strategy(data, n=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['momentum'] = data['close'].pct_change(periods=n)
    signals['signal'][n:] = np.where(signals['momentum'][n:] > 0, 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# 数据准备
data = pd.read_csv('data.csv', index_col=0, parse_dates=True)
data = data.dropna()

# 调用策略函数
signals_ma = moving_average_strategy(data)
signals_momentum = momentum_strategy(data)

# 组合策略
signals = pd.DataFrame(index=data.index)
signals['signal'] = signals_ma['signal'] + signals_momentum['signal']
signals['positions'] = signals['signal'].diff()


======================================================

#均线策略：在数据处理和均线周期的选择上，有很大的优化空间。
def moving_average_strategy(data, short_window=5, long_window=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

#动量策略：选择合适的动量周期和参数，以及筛选出具有良好动量的品种。
def momentum_strategy(data, n=10):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['momentum'] = data['close'].pct_change(periods=n)
    signals['signal'][n:] = np.where(signals['momentum'][n:] > 0, 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

#日内交易策略：根据不同市场的交易时间段，选择适合的日内交易策略。
def intraday_strategy(data, hour_start=10, hour_end=14):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['signal'][(data.index.hour >= hour_start) & (data.index.hour <= hour_end)] = 1.0
    signals['positions'] = signals['signal'].diff()
    return signals

#突破交易策略：优化突破周期和阈值等参数，筛选出具有良好突破特征的品种。
def breakout_strategy(data, n=20):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['high'] = data['high'].rolling(window=n, min_periods=1, center=False).max()
    signals['low'] = data['low'].rolling(window=n, min_periods=1, center=False).min()
    signals['signal'] = np.where(data['close'] > signals['high'], 1.0, np.where(data['close'] < signals['low'], -1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

#反转交易策略：优化反转周期和阈值等参数，以及筛选出具有良好反转特征的品种。

#套利策略：根据不同品种之间的价差关系，选择适合的套利策略。
def arbitrage_strategy(data1, data2, n=10):
    signals = pd.DataFrame(index=data1.index)
    signals['signal'] = 0.0
    signals['spread'] = data1['close'] - data2['close']
    signals['zscore'] = (signals['spread'] - signals['spread'].rolling(window=n).mean()) / signals['spread'].rolling(window=n).std()
    signals['signal'] = np.where(signals['zscore'] > 1.0, -1.0, np.where(signals['zscore'] < -1.0, 1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

#多空策略：利用不同品种或者同一品种的不同合约，建立多空仓位的对冲策略。
def long_short_strategy(data1, data2, n=10):
    signals = pd.DataFrame(index=data1.index)
    signals['signal'] = 0.0
    signals['long_mavg'] = data1['close'].rolling(window=n, min_periods=1, center=False).mean()
    signals['short_mavg'] = data2['close'].rolling(window=n, min_periods=1, center=False).mean()
    signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, np.where(signals['short_mavg'] < signals['long_mavg'], -1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

#时间序列模型策略：利用时间序列模型预测未来价格走势，选择适合的模型和参数。
def arima_strategy(data, p=0, d=1, q=1):
    from statsmodels.tsa.arima_model import ARIMA
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    model = ARIMA(data['close'].values, order=(p, d, q))
    results = model.fit()
    signals['signal'] = np.where(results.forecast()[0] > data['close'].iloc[-1], 1.0, -1.0)
    signals['positions'] = signals['signal'].diff()
    return signals

#机器学习策略：利用机器学习算法训练模型预测未来价格走势，选择适合的算法和参数。
def machine_learning_strategy(data, features=['open', 'high', 'low', 'volume'], target='close'):
    from sklearn.ensemble import RandomForestClassifier
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    model = RandomForestClassifier(n_estimators=100)
    X = data[features]
    y = np.where(data[target].shift(-1) > data[target], 1, -1)
    model.fit(X[:-1], y[:-1])
    signals['signal'] = np.where(model.predict(X.iloc[-1:].values) > 0, 1.0, -1.0)
    signals['positions'] = signals['signal'].diff()
   
#基本面分析策略：根据基本面数据分析公司或者市场的价值，选择适合的投资策略。
def fundamental_analysis_strategy(data, features=['market_cap', 'pe_ratio', 'dividend_yield'], target='close'):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['signal'][data[features].mean(axis=1) > data[features].mean().mean()] = 1.0
    signals['positions'] = signals['signal'].diff()
    return signals
