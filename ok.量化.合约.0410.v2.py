#例程序的基础上，我们可以添加一些额外功能，例如动态调整交易参数、实现更复杂的交易策略或添加日志记录。

import okex.Account_api as Account
import okex.Trade_api as Trade
import okex.public_api as Public
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置API密钥和秘钥
api_key = 'your_api_key'
secret_key = 'your_secret_key'
passphrase = 'your_passphrase'

# 初始化API对象
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False)
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False)
publicAPI = Public.PublicAPI(False)

# 设置交易参数
symbol = 'BTC-USDT-SWAP'  # 合约品种
leverage = 20  # 杠杆倍数
amount = 1  # 开仓数量
profit_target = 1.005  # 目标收益率
stop_loss = 0.995  # 止损率
order_interval = 5  # 下单间隔（秒）

def place_orders():
    # 获取最新价格
    ticker = publicAPI.get_ticker(symbol)
    if not ticker or 'best_ask' not in ticker:
        logger.error("Failed to get ticker.")
        return

    current_price = float(ticker['best_ask'])

    # 计算止盈止损价格
    take_profit_price = current_price * profit_target
    stop_loss_price = current_price * stop_loss

    # 设置杠杆
    tradeAPI.set_leverage(symbol, leverage)

    # 买入开多
    tradeAPI.place_order(symbol, 'buy', str(current_price), str(amount))

    # 设置止盈止损
    tradeAPI.place_order(symbol, 'sell', str(take_profit_price), str(amount), 'limit', 'reduce_only')
    tradeAPI.place_order(symbol, 'sell', str(stop_loss_price), str(amount), 'limit', 'reduce_only')

    logger.info(f"Opened position at {current_price}, take profit: {take_profit_price}, stop loss: {stop_loss_price}")

if __name__ == "__main__":
    while True:
        place_orders()
        time.sleep(order_interval)
