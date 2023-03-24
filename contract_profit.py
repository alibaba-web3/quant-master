import os

import matplotlib.pyplot as plt
import pandas as pd
from function import *

# 示例策略：协议手续费 上升时买入并持有 1 天

# 每次投入金额
invest = 100
symbol = "UNI"
# 手续费
fee = 0.0004


# 读取整理数据
def read_data():
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))

    # 读取所有现货数据
    spotPath = root_path + '/data/spot_1d.csv'
    profitPath = root_path + '/data/profit_1d.csv'

    spotDf = pd.read_csv(spotPath, encoding='utf-8', skiprows=0)
    profitDf = pd.read_csv(profitPath, encoding='utf-8', skiprows=0)

    profitDf = profitDf[profitDf["symbol"] == symbol]
    profitDf = profitDf.sort_values(by=['date'])

    profitDf["symbol"] = profitDf[["symbol"]].apply(lambda x: x + "USDT")
    profitDf["date"] = pd.to_datetime(profitDf["date"]).dt.date

    spotDf = spotDf[spotDf["symbol"] == symbol + "USDT"]
    spotDf["date"] = pd.to_datetime(spotDf["openTime"]).dt.date

    # 删除不需要的数据
    spotDf.drop(
        columns=['buyingTurnover', 'buyingVolume', 'openTime', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
        inplace=True)

    # 合约利润数据和价格数据整理
    df = pd.merge(spotDf, profitDf, on=["date", "symbol"])
    return df


# 策略实现
def strategy(df):
    # 回测策略：协议手续费 上升时买入并持有 1 天
    df["feeUp"] = df["total_fees"] - df["total_fees"].shift(-1)
    df.dropna(axis=0, how='any', inplace=True)
    df["invest"] = df[["feeUp"]].iloc[:, 0].apply(lambda x: 100 if x > 0 else 0)

    df.loc[df['feeUp'] >= 0, 'invest'] = 100
    df.loc[df['feeUp'] < 0, 'invest'] = 0

    df.loc[df['invest'] > 0, 'currentRevenueRate'] = (df["close"].shift(-1) - df["close"]) / df["close"] - fee * 2

    df["totalInvest"] = df["invest"].cumsum()
    df["revenueRate"] = df["currentRevenueRate"].cumsum()

    # 补充空缺的数据
    df["revenueRate"] = df["revenueRate"].fillna(method='pad')
    return df


def main():
    # TVL 数据和价格数据整理
    df = read_data()

    # 回测策略：协议手续费 上升时买入并持有 1 天
    df = strategy(df)

    # 策略分析
    analyze_strategy(df)

    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()
