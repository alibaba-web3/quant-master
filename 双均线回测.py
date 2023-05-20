import os

import pandas as pd

from function import *

# 示例策略：BTC 定投

# 每天定投金额
invest = 100
fee = 0.0006
start_date = '2023-01-01'
end_date = '2024-01-01'

root_path = os.path.abspath(os.path.dirname(__file__))


# 读取整理数据
def read_data(s):
    # 返回当前文件路径
    path = root_path + '/data/binance/1h/' + s + '-1h.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)

    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    # 选择时间范围
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

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
    short_rolling = df['close'].rolling(window=shortEma).mean()
    long_rolling = df['close'].rolling(window=longEma).mean()

    # 创建一个signal列，当短期平均线上穿长期平均线时设置为1，下穿时设置为-1
    df['signal'] = 0
    df.loc[short_rolling > long_rolling, 'signal'] = -1
    df.loc[short_rolling < long_rolling, 'signal'] = 1

    # 计算日收益
    df['daily_return'] = df['close'].pct_change()

    # 计算策略收益
    df['strategy_return'] = df['signal'].shift() * df['daily_return']

    # 计算手续费
    df.loc[df['signal'] * df['signal'].shift() == -1, 'fee'] = fee * 2
    df.loc[df['signal'] * df['signal'].shift() == 1, 'fee'] = 0
    df['fee'] = np.where((df['signal'] * df['signal'].shift() == 0) & (df['signal'] != 0), 0, df['fee'])
    df['fee'] = df['fee'].fillna(0)

    df['strategy_return'] = df['strategy_return'] - df['fee']

    # 计算累计收益
    df['cumulative_market_returns'] = np.cumprod(1 + df['daily_return'])
    # df['cumulative_strategy_returns'] = np.cumprod(1 + df['strategy_return'])
    df['cumulative_strategy_returns'] = np.cumsum(df['strategy_return'])
    df['cumulative_fee'] = np.cumsum(df['fee'])

    df["revenueRate"] = df['cumulative_strategy_returns']
    # df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    revenue = df["revenueRate"].iloc[-1]
    fee_rate = df["cumulative_fee"].iloc[-1]
    if revenue > 0.2:
        print(f"{shortEma} {longEma} {symbol} 最终收益率：", revenue)
    # print(f" {shortEma} {longEma} {symbol} 最终收益率：{format(revenue, '.3f')}, 手续费 {format(fee_rate, '.3f')}")
    return revenue, fee_rate


def main(s):
    # 读取数据
    df = read_data(s)
    # 策略逻辑
    revenue, fee_rate = strategy(df)
    # 策略分析
    # analyze_strategy(df)
    # 资金曲线
    # df.plot('date', y=['revenueRate'])
    # plt.show()

    return revenue, fee_rate


# 获取文件夹下所有文件名
total_revenue = 0
total_fee = 0
for root, dirs, files in os.walk(root_path + '/data/binance/1h/'):
    shortEma = 5
    longEma = 20
    for file in files:
        if file.endswith(".csv"):
            symbol = file.split("-1h")[0]
            revenue, fee_rate = main(symbol)
            total_revenue += revenue
            total_fee += fee_rate

# main('BTC-USDT')

# for shortEma in range(4, 7):
#     for longEma in range(shortEma + 15, 30):
#         revenue, fee_rate = main('BNB-USDT')
#         total_revenue += revenue
#         total_fee += fee_rate

print("总收益率：", total_revenue, "总手续费：", total_fee)
