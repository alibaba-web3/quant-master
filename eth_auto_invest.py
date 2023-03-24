import os

import pandas as pd
import matplotlib.pyplot as plt
from function import *

# 初始投资金额
invest = 100


def read_data():
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))
    # 读取所有现货数据
    path = root_path + '/data/spot_1d.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)
    # 删除不需要的数据
    df.drop(
        columns=['buyingTurnover', 'buyingVolume', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
        inplace=True)
    # 只保留 ETH 数据
    df = df[df['symbol'] == "ETHUSDT"]
    df["date"] = pd.to_datetime(df["openTime"])
    return df


# 交易策略函数
def strategy(df):
    # 每天收盘价格变化
    df["close变化"] = df["close"] - df["close"].shift(-1)
    # 删除包含任意一个缺失值的列
    df.dropna(axis=0, how='any', inplace=True)

    df.loc[df['close变化'] <= 0, 'invest'] = invest * 0.3
    df.loc[df['close变化'] > 0, 'invest'] = invest
    df.loc[df['invest'] > 0, 'currentRevenueRate'] = (df["close"].shift(-1) - df["close"]) / df["close"]

    df["累计投资"] = df["invest"].cumsum()
    df["revenueRate"] = df["currentRevenueRate"].cumsum()
    # 补充空缺的数据
    df["revenueRate"] = df["revenueRate"].fillna(method='pad')
    return df


def main():
    # 数据整理
    df = read_data()

    # 回测策略
    df = strategy(df)

    # 策略分析
    analyze_strategy(df)

    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()
