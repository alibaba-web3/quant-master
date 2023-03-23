import os

import pandas as pd
import matplotlib.pyplot as plt
from function import *

# 返回当前文件路径
root_path = os.path.abspath(os.path.dirname(__file__))

# 读取历史现货价格数据
spotPath = root_path + '/data/spot_1d.csv'
df = pd.read_csv(spotPath)
df['date'] = pd.to_datetime(df['openTime'])

# 删除多余数据列
df.drop(
    columns=['buyingTurnover', 'buyingVolume', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
    inplace=True)

# 保留 ETH 数据
df = df[df['symbol'] == 'BTCUSDT']

# 初始投资金额
invest = 100

# 交易策略函数
def trading_strategy(df, invest):
    # 每天收盘价格变化
    df["close变化"] = df["close"] - df["close"].shift(-1)
    # 删除包含任意一个缺失值的列
    df.dropna(axis=0, how='any', inplace=True)

    df.loc[df['close变化'] <= 0, '当天投资'] = invest * 0.3
    df.loc[df['close变化'] > 0, '当天投资'] = invest
    df.loc[df['当天投资'] > 0, '本次盈亏'] = (df["close"].shift(-1) - df["close"]) / df["close"]

    df["累计投资"] = df["当天投资"].cumsum()
    df["revenueRate"] = df["本次盈亏"].cumsum()
    # 补充空缺的数据
    df["revenueRate"] = df["revenueRate"].fillna(method='pad')
    return df

# 调用交易策略函数
df = trading_strategy(df, invest)

# 策略分析
analyze_strategy(df)

# 资金曲线
df.plot('date', y=['revenueRate'])
plt.show()
