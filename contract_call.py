import os

import matplotlib.pyplot as plt
import pandas as pd
from function import *

# 示例策略：transfer 上升时买入并持有 1 天

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
    erc20UserPath = root_path + '/data/erc20_user_1d.csv'

    spotDf = pd.read_csv(spotPath, encoding='utf-8', skiprows=0)
    erc20UserDf = pd.read_csv(erc20UserPath, encoding='utf-8', skiprows=0)

    erc20UserDf = erc20UserDf[erc20UserDf["symbol"] == symbol]
    erc20UserDf = erc20UserDf.sort_values(by=['time'])

    erc20UserDf["symbol"] = erc20UserDf[["symbol"]].apply(lambda x: x + "USDT")
    erc20UserDf["date"] = pd.to_datetime(erc20UserDf["time"]).dt.date

    spotDf = spotDf[spotDf["symbol"] == symbol + "USDT"]
    spotDf["date"] = pd.to_datetime(spotDf["openTime"]).dt.date

    # 删除不需要的数据
    spotDf.drop(
        columns=['buyingTurnover', 'buyingVolume', 'openTime', 'closeTime', 'tradingVolume', 'turnover', 'volume'],
        inplace=True)
    erc20UserDf.drop(columns=['contract_address', 'time'], inplace=True)

    # 合约调用数据和价格数据整理
    df = pd.merge(spotDf, erc20UserDf, on=["date", "symbol"])

    return df


# 策略实现
def strategy(df):
    # 回测策略：TVL 相比昨天上升则买入并持有 1 天
    df["transferUp"] = df["transfer_count"] - df["transfer_count"].shift(-1)
    df.dropna(axis=0, how='any', inplace=True)
    df["invest"] = df[["transferUp"]].iloc[:, 0].apply(lambda x: 100 if x > 0 else 0)

    df.loc[df['transferUp'] >= 0, 'invest'] = 100
    df.loc[df['transferUp'] < 0, 'invest'] = 0

    df.loc[df['invest'] > 0, '本次盈亏'] = (df["close"].shift(-1) - df["close"]) / df["close"] - fee * 2

    df["totalInvest"] = df["invest"].cumsum()
    df["revenueRate"] = df["本次盈亏"].cumsum()

    # 补充空缺的数据
    df["revenueRate"] = df["revenueRate"].fillna(method='pad')

    return df


def main():
    # 数据整理
    df = read_data()

    # 回测策略：TVL 相比昨天上升则买入并持有 1 天
    df = strategy(df)

    # 策略分析
    analyze_strategy(df)

    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()


main()
