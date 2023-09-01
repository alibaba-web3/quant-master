import os

import pandas as pd
from matplotlib import pyplot as plt

from function import *

# 单次交易金额
invest = 10000
fee = 0.0004 + 0.0003 + 0.0002
timeframe = '1h'
select = []

root_path = os.path.abspath(os.path.dirname(__file__))
ohlcv_dir_path = root_path + '/data/binance/' + timeframe + '/'

start_date = '2021-01-01'
end_date = '2024-01-01'


# 读取整理数据
def read_data(symbol):
    # 返回当前文件路径
    path = ohlcv_dir_path + symbol + '-' + timeframe + '.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)

    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    # 选择时间范围
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    return df


# 策略实现
def strategy(df, ma):
    spread = 0.001

    df['ma'] = df['close'].rolling(window=ma).mean()
    df['maTop'] = df['ma'] * (1 + spread * 2)
    df['maBottom'] = df['ma'] * (1 - spread * 2)

    df['signal'] = -1
    # 没有均线价格
    df.loc[df['ma'].shift().isnull(), 'signal'] = 0
    # 价格没有碰到均线
    df.loc[df['low'] > df['ma'].shift(), 'signal'] = 0
    df.loc[df['high'] < df['ma'].shift(), 'signal'] = 0
    # 价格上穿均线
    df.loc[(df['low'] < df['ma'].shift()) & (df['high'] > df['ma'].shift()) & (
            df['high'] > df['maTop'].shift()), 'signal'] = 1
    # 价格下穿均线
    df.loc[(df['low'] < df['ma'].shift()) & (df['high'] > df['ma'].shift()) & (
            df['low'] < df['maBottom'].shift()), 'signal'] = 1

    # 计算手续费
    df.loc[df['signal'] != 0, 'fee'] = fee
    df['fee'] = df['fee'].fillna(0)

    df.loc[df['signal'] != 0, 'invest'] = invest
    df['invest'] = df['invest'].fillna(0)

    df.loc[df['signal'] == 0, 'revenue'] = 0
    df.loc[df['signal'] == 1, 'revenue'] = spread - df['fee']
    df.loc[df['signal'] == -1, 'revenue'] = -(abs(df['close'] - df['ma'].shift())) / df['ma'].shift() - df[
        'fee'] - 0.0007 - 0.0002

    # 计算累计收益
    df['revenueRate'] = np.cumsum(df['revenue'])
    df['cumulative_fee'] = np.cumsum(df['fee'])


def main(symbol, ma):
    # 读取数据
    df = read_data(symbol)
    if df.empty:
        return 0, 0
    # 策略逻辑
    strategy(df, ma)
    # 策略分析
    analyze_strategy(df)

    # df = df[df['signal'] == -1]
    # df['r'] = df['revenue'].mean()

    # if revenue_rate > 0:
    #     select.append(symbol)
    #     print(symbol, revenue_rate, max_drawdown)

    # 资金曲线
    df.plot('date', y=['revenueRate'])
    # 设置图表名称
    plt.title(symbol)
    plt.show()


main('DOGE-USDT', 20)
# for i in range(1, 10000):
#     main('BTC-USDT', i)
