import os

import pandas as pd
from matplotlib import pyplot as plt

from function import *

# 单次交易金额
invest = 10000
fee = 0.0006
timeframe = '4h'
select = []

root_path = os.path.abspath(os.path.dirname(__file__))
ohlcv_dir_path = root_path + '/data/binance/' + timeframe + '/'

# 读取整理数据
def read_data(symbol, start_date, end_date):
    # 返回当前文件路径
    path = ohlcv_dir_path + symbol + '-' + timeframe + '.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)

    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    # 选择时间范围
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    return df


# 策略实现
def strategy(df, ma, reverse=False):
    ma_rolling = df['close'].rolling(window=ma).mean()
    close = df['close']

    # 创建一个signal列，当短期平均线上穿长期平均线时设置为1，下穿时设置为-1
    df['signal'] = 0
    if reverse:
        df.loc[ma_rolling > close, 'signal'] = -1
        df.loc[ma_rolling < close, 'signal'] = 1
    else:
        df.loc[ma_rolling > close, 'signal'] = 1
        df.loc[ma_rolling < close, 'signal'] = -1

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

    # if revenue > 0.2:
    #     print(f"{s} 最终收益率：", format(revenue, '.3f'))
    #     select.append(s.replace('-', ''))

    # print(f" {shortEma} {longEma} {symbol} 最终收益率：{format(revenue, '.3f')}, 手续费 {format(fee_rate, '.3f')}")
    return revenue, fee_rate


def main(s, ma, reverse=False, start_date='2020-01-01', end_date='2024-01-01'):
    # 读取数据
    df = read_data(s, start_date, end_date)
    if df.empty:
        return 0, 0
    # 策略逻辑
    revenue, fee_rate = strategy(df, ma, reverse)
    # 策略分析
    # analyze_strategy(df)

    # # 资金曲线
    # df.plot('date', y=['revenueRate'])
    # # 设置图表名称
    # plt.title(s)
    # plt.show()

    return revenue, fee_rate


# main('BTC-USDT', 20)

# 回测所有的币

# symbol = 'UNI-USDT'
ma = 20
holdDays = 90


# 从 2021 开始回测，每周遍历一次
def backtest(symbol):
    total_revenue = 0
    total_fee = 0
    start_date = '2021-01-01'
    for i in range(1, 53 * 3):
        end_date = (pd.to_datetime(start_date) + pd.Timedelta(days=holdDays)).strftime('%Y-%m-%d')

        # 上周开始时间
        last_week_start_date = (pd.to_datetime(start_date) - pd.Timedelta(days=holdDays)).strftime('%Y-%m-%d')
        # 上周回测结果
        last_week_revenue_true, last_week_fee_true = main(symbol, ma, True, last_week_start_date, start_date)
        # last_week_revenue_false, last_week_fee_false = main(symbol, ma, False, last_week_start_date, start_date)

        if last_week_revenue_true > 0.00:
            revenue, fee_rate = main(symbol, ma, False, start_date, end_date)
            total_revenue += revenue
            total_fee += fee_rate

            start_date = (pd.to_datetime(start_date) + pd.Timedelta(days=holdDays)).strftime('%Y-%m-%d')
        # elif last_week_revenue_false > 0.00:
        # 本周回测结果
        # start_date = (pd.to_datetime(start_date) + pd.Timedelta(days=holdDays)).strftime('%Y-%m-%d')
        else:
            start_date = (pd.to_datetime(start_date) + pd.Timedelta(days=holdDays)).strftime('%Y-%m-%d')
            continue

    print(symbol, total_revenue, total_fee)
    return total_revenue, total_fee


# total_revenue, total_fee = backtest(symbol)
# print(symbol, total_revenue, total_fee)

# 回测所有交易对
total_revenue = 0
total_fee = 0
for root, dirs, files in os.walk(ohlcv_dir_path):

    for file in files:
        if file.endswith(".csv"):
            symbol = file.split("-" + timeframe)[0]
            revenue, fee_rate = backtest(symbol)
            total_revenue += revenue
            total_fee += fee_rate

print("总收益率：", format(total_revenue, '.3f'), "总手续费：", format(total_fee, '.3f'))
