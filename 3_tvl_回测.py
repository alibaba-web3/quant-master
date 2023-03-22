import os

import matplotlib.pyplot as plt
import pandas as pd
from function import *

# 示例策略：TVL 相比昨天上升则买入并持有 1 天

# 每次投入金额
invest = 100
symbol = "MKR"


# 读取整理数据
def read_data():
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))

    # 读取所有现货数据
    spotPath = root_path + '/data/spot_1d.csv'
    tvlPath = root_path + '/data/tvl.csv'

    spotDf = pd.read_csv(spotPath, encoding='utf-8', skiprows=0)
    tvlDf = pd.read_csv(tvlPath, encoding='utf-8', skiprows=0)

    tvlDf = tvlDf[tvlDf["symbol"] == symbol]
    tvlDf = tvlDf[tvlDf["symbol"] != "-"]
    tvlDf["symbol"] = tvlDf[["symbol"]].apply(lambda x: x + "USDT")
    tvlDf["date"] = pd.to_datetime(tvlDf["date"])

    spotDf = spotDf[spotDf["symbol"] == symbol + "USDT"]
    spotDf["date"] = pd.to_datetime(spotDf["openTime"])

    # 删除不需要的数据
    spotDf.drop(
        columns=['buyingTurnover', 'buyingVolume', 'openTime', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
        inplace=True)
    tvlDf.drop(columns=['name'],
               inplace=True)

    # TVL 数据和价格数据整理
    return pd.merge(spotDf, tvlDf, on=["date", "symbol"])


# 策略实现
def strategy(df):
    # 回测策略：TVL 相比昨天上升则买入并持有 1 天
    df["tvl变化"] = df["tvl"] - df["tvl"].shift(-1)
    df.dropna(axis=0, how='any', inplace=True)

    df.loc[df['tvl变化'] <= 0, '当天投资'] = 0
    df.loc[df['tvl变化'] > 0, '当天投资'] = invest

    df.loc[df['当天投资'] > 0, '本次盈亏'] = (df["close"].shift(-1) - df["close"]) / df["close"]

    df["累计投资"] = df["当天投资"].cumsum()
    df["revenueRate"] = df["本次盈亏"].cumsum()

    # 补充空缺的数据
    df["revenueRate"] = df["revenueRate"].fillna(method='pad')

    return df


def main():
    # TVL 数据和价格数据整理
    df = read_data()

    # 回测策略：TVL 相比昨天上升则买入并持有 1 天
    df = strategy(df)

    # 策略分析
    analyze_strategy(df)

    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()
