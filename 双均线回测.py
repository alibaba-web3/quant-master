import os

import matplotlib.pyplot as plt
import pandas as pd
from function import *

# 示例策略：BTC 定投

# 每天定投金额
invest = 100


# 读取整理数据
def read_data():
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))

    # 读取所有现货数据
    path = root_path + '/data/binance/1h/ETH-USDT-1h.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)

    return df

    # df1 = df[df['symbol'] == "CRVUSDT"]
    # df2 = df[df['symbol'] == "CVXUSDT"]
    #
    # df3 = df1.merge(df2, on='date', how='left')
    #
    # df3['close'] = df3['close_y'] / df3['close_x']
    # df3['openTime'] = df3['openTime_x']
    #
    # return df3


# 策略实现
def strategy(df):
    short_rolling = df['close'].rolling(window=5).mean()
    long_rolling = df['close'].rolling(window=20).mean()

    # 创建一个signal列，当短期平均线上穿长期平均线时设置为1，下穿时设置为-1
    df['signal'] = 0
    df.loc[short_rolling > long_rolling, 'signal'] = 1
    df.loc[short_rolling < long_rolling, 'signal'] = -1

    # 计算日收益
    df['daily_return'] = df['close'].pct_change()

    # 计算策略收益
    df['strategy_return'] = df['signal'].shift() * df['daily_return']

    # 计算累计收益
    df['cumulative_market_returns'] = np.cumprod(1 + df['daily_return'])
    df['cumulative_strategy_returns'] = np.cumprod(1 + df['strategy_return'])

    # 回测策略：BTC 定投
    df["revenueRate"] = df['cumulative_strategy_returns']
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date


def main():
    # 读取数据
    df = read_data()
    # 策略逻辑
    strategy(df)
    # 策略分析
    # analyze_strategy(df)
    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()
