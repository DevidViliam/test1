
import ccxt
import time
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
import threading

# Initialize the ccxt library with the chosen exchange
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret',
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
timeframe = '1m'
app = Flask(__name__)

def get_ticker():
    ticker = exchange.fetch_ticker(symbol)
    return ticker

def get_order_book(depth=10):
    order_book = exchange.fetch_order_book(symbol, limit=depth)
    return order_book

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe_ratio

def calculate_maximum_drawdown(returns):
    cumulative_returns = [1 + r for r in returns]
    for i in range(1, len(cumulative_returns)):
        cumulative_returns[i] *= cumulative_returns[i - 1]

    max_drawdown = 0
    peak_value = cumulative_returns[0]
