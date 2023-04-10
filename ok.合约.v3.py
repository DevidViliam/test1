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
ma_period = 20  # 移动平均周期

def calculate_moving_average(period):
    candles = publicAPI.get_candles(symbol, period, 60)
    if not candles:
        logger.error("Failed to get candles.")
        return None

    prices = [float(candle[4]) for candle in candles]
    moving_average = sum(prices) / period

    return moving_average

def place_orders(side, current_price):
    # 计算止盈止损价格
    take_profit_price = current_price * (profit_target if side == 'buy' else 1 / profit_target)
    stop_loss_price = current_price * (stop_loss if side == 'buy' else 1 / stop_loss)

    # 设置杠杆
    tradeAPI.set_leverage(symbol, leverage)

    # 下单
    tradeAPI.place_order(symbol, side, str(current_price), str(amount))

    # 设置止盈止损
    tradeAPI.place_order(symbol, 'sell' if side == 'buy' else 'buy', str(take_profit_price), str(amount), 'limit', 'reduce_only')
    tradeAPI.place_order(symbol, 'sell' if side == 'buy' else 'buy', str(stop_loss_price), str(amount), 'limit', 'reduce_only')

    logger.info(f"Opened {side} position at {current_price}, take profit: {take_profit_price}, stop loss: {stop_loss_price}")

if __name__ == "__main__":
    while True:
        # 获取最新价格
        ticker = publicAPI.get_ticker(symbol)
        if not ticker or 'best_ask' not in ticker:
            logger.error("Failed to get ticker.")
            continue

        current_price = float(ticker['best_ask'])
        moving_average = calculate_moving_average(ma_period)

        if moving_average is None:
            logger.error("Failed to calculate moving average.")
            continue

        if current_price > moving_average:
            place_orders('buy', current_price)
        else:
            place_orders('sell', current_price)

        time.sleep(order_interval)

