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
    path = root_path + '/data/spot_1d.csv'
    df = pd.read_csv(path, encoding='utf-8', skiprows=0)

    # 删除不需要的数据
    df.drop(
        columns=['buyingTurnover', 'buyingVolume', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
        inplace=True)

    # 只保留 BTC 数据
    df = df[df['symbol'] == "BTCUSDT"]

    return df


# 策略实现
def strategy(df):
    # 回测策略：BTC 定投
    df["invest"] = invest
    df["当天买入BTC"] = df[["open"]].apply(lambda x: invest / x["open"], axis=1)
    df["累计BTC"] = df["当天买入BTC"].cumsum()
    df["totalInvest"] = df["invest"].cumsum()
    df["balance"] = df[["累计BTC", "close"]].apply(lambda x: x["累计BTC"] * x["close"], axis=1)
    df['revenue'] = df[["balance", "totalInvest"]].apply(lambda x: x["balance"] - x["totalInvest"], axis=1)
    df["revenueRate"] = df[["revenue", "totalInvest"]].apply(lambda x: x["revenue"] / x["totalInvest"], axis=1)
    df["date"] = pd.to_datetime(df["openTime"]).dt.date


def main():
    # 读取数据
    df = read_data()
    # 策略逻辑
    strategy(df)
    # 策略分析
    analyze_strategy(df)
    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()

