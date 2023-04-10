
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime

def moving_average(data, window):
    return data.rolling(window=window).mean()

def RSI(data, window=14):
    delta = data.diff()
    gain, loss = delta.copy(), delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = abs(loss.rolling(window=window).mean())

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2022, 1, 1)
ticker = 'AAPL'

# 获取股票数据
data = web.DataReader(ticker, 'yahoo', start_date, end_date)
data['MA50'] = moving_average(data['Close'], 50)
data['RSI'] = RSI(data['Close'])

# 设定交易信号
data['Signal'] = 0
data.loc[(data['Close'] > data['MA50']) & (data['RSI'] < 30), 'Signal'] = 1
data.loc[(data['Close'] < data['MA50']) & (data['RSI'] > 70), 'Signal'] = -1

# 计算策略收益
data['Position'] = data['Signal'].cumsum()
data['Strategy_Return'] = data['Close'].pct_change() * data['Position']

# 输出策略收益
print('策略收益：', data['Strategy_Return'].cumsum()[-1])



import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime

def Bollinger_Bands(data, window=20, num_std=2):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()

    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)

    return upper_band, lower_band

start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2022, 1, 1)
ticker = 'AAPL'

# 获取股票数据
data = web.DataReader(ticker, 'yahoo', start_date, end_date)
data['Upper_BB'], data['Lower_BB'] = Bollinger_Bands(data['Close'])

# 设定交易信号
data['Signal'] = 0
data.loc[data['Close'] < data['Lower_BB'], 'Signal'] = 1
data.loc[data['Close'] > data['Upper_BB'], 'Signal'] = -1

# 计算策略收益
data['Position'] = data['Signal'].cumsum()
data['Strategy_Return'] = data['Close'].pct_change() * data['Position']

# 输出策略收益
print('策略收益：', data['Strategy_Return'].cumsum()[-1])


import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime

def zscore(series):
    return (series - series.mean()) / np.std(series)

start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2022, 1, 1)
ticker1 = 'AAPL'
ticker2 = 'MSFT'

# 获取股票数据
data1 = web.DataReader(ticker1, 'yahoo', start_date, end_date)['Close']
data2 = web.DataReader(ticker2, 'yahoo', start_date, end_date)['Close']

# 计算价差
spread = data1 - data2
zscore_spread = zscore(spread)

# 设定交易信号
threshold = 1.5
signal = pd.Series(index=zscore_spread.index)
signal[zscore_spread > threshold] = -1
signal[zscore_spread < -threshold] = 1

# 计算策略收益
position = signal.shift(1).fillna(0).cumsum()
strategy_return = (data1.pct_change() - data2.pct_change()) * position

# 输出策略收益
print('策略收益：', strategy_return.cumsum()[-1])
