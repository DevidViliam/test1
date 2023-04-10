
import time
import okx

# 替换为您的API密钥和密钥
api_key = 'your_api_key'
secret_key = 'your_secret_key'
passphrase = 'your_passphrase'

# 初始化OKX客户端
client = okx.Client(api_key, secret_key, passphrase)

# 交易参数
symbol = 'BTC-USDT'
trade_interval = 5  # 以秒为单位的交易间隔

def get_market_price(symbol):
    ticker = client.get_ticker(symbol)
    return float(ticker['last'])

def place_order(symbol, side, order_type, size, price=None):
    order = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        size=size,
        price=price
    )
    return order

def simple_trading_strategy(symbol, trade_interval):
    while True:
        try:
            # 获取市场价格
            market_price = get_market_price(symbol)

            # 交易策略逻辑
            if market_price > 10000:
                side = 'sell'
            else:
                side = 'buy'

            # 下单
            order = place_order(symbol, side, 'market', 0.001)
            print(f'下单成功：{order}')

            # 等待下次交易
            time.sleep(trade_interval)
        except Exception as e:
            print(f'交易出错：{e}')
            time.sleep(trade_interval)

if __name__ == '__main__':
    simple_trading_strategy(symbol, trade_interval)
