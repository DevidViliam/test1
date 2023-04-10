import time
import okx

# 替换为您的API密钥和密钥
api_key = 'your_api_key'
secret_key = 'your_secret_key'
passphrase = 'your_passphrase'

# 初始化OKX客户端
client = okx.Client(api_key, secret_key, passphrase)

# 交易参数
symbol = 'BTC-USDT-220325'
trade_interval = 60  # 以秒为单位的交易间隔
leverage = 10  # 使用10倍杠杆
max_position = 0.01  # 最大持仓量

def get_market_price(symbol):
    ticker = client.get_ticker(symbol)
    return float(ticker['last'])

def set_leverage(symbol, leverage):
    client.set_leverage(symbol, leverage)

def get_position(symbol):
    position = client.get_position(symbol)
    return float(position['size'])

def place_order(symbol, side, order_type, size, price=None):
    order = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        size=size,
        price=price
    )
    return order

def trading_strategy(symbol, trade_interval, leverage, max_position):
    set_leverage(symbol, leverage)
    
    while True:
        try:
            # 获取市场价格
            market_price = get_market_price(symbol)

            # 获取当前持仓量
            current_position = get_position(symbol)

            # 交易策略逻辑
            if market_price > 10000 and current_position <= max_position:
                side = 'sell'
                size = min(max_position - current_position, 0.001)
            elif market_price <= 10000 and current_position >= -max_position:
                side = 'buy'
                size = min(max_position + current_position, 0.001)
            else:
                print("持仓已达最大限制，暂停交易")
                time.sleep(trade_interval)
                continue

            # 下单
            order = place_order(symbol, side, 'limit', size, market_price)
            print(f'下单成功：{order}')

            # 等待下次交易
            time.sleep(trade_interval)
        except Exception as e:
            print(f'交易出错：{e}')
            time.sleep(trade_interval)

if __name__ == '__main__':
    trading_strategy(symbol, trade_interval, leverage, max_position)
