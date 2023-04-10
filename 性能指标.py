
#Sharpe Ratio:
import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe_ratio

#Maximum Drawdown:
def calculate_maximum_drawdown(returns):
    cumulative_returns = [1 + r for r in returns]
    for i in range(1, len(cumulative_returns)):
        cumulative_returns[i] *= cumulative_returns[i - 1]

    max_drawdown = 0
    peak_value = cumulative_returns[0]

    for i in range(1, len(cumulative_returns)):
        if cumulative_returns[i] > peak_value:
            peak_value = cumulative_returns[i]
        else:
            drawdown = (peak_value - cumulative_returns[i]) / peak_value
            max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown

#Return on Investment (ROI):
def calculate_roi(initial_investment, final_value):
    roi = (final_value - initial_investment) / initial_investment
    return roi
