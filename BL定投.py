import os

import matplotlib.pyplot as plt
import pandas as pd
from function import *

# 示例策略：BTC 定投

# 每天定投金额
invest = 100
long = "BTC-USDT"
short = "LTC-USDT"
timeframe = "1d"

root_path = os.path.abspath(os.path.dirname(__file__))
ohlcv_dir_path = root_path + '/data/binance/' + timeframe + '/'


# 读取整理数据
def read_data():
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))

    # 读取所有现货数据
    longPath = ohlcv_dir_path + long + '-' + timeframe + '.csv'
    longDf = pd.read_csv(longPath, encoding='utf-8', skiprows=0)
    shortPath = ohlcv_dir_path + short + '-' + timeframe + '.csv'
    shortDf = pd.read_csv(shortPath, encoding='utf-8', skiprows=0)

    longDf["date"] = pd.to_datetime(longDf["timestamp"]).dt.date
    shortDf["date"] = pd.to_datetime(shortDf["timestamp"]).dt.date

    # 删掉不需要的数据
    longDf.drop(['open', 'high', 'low', 'volume', 'timestamp'], axis=1, inplace=True)
    shortDf.drop(['open', 'high', 'low', 'volume', 'timestamp'], axis=1, inplace=True)

    # 按照时间合并数据
    result = pd.merge(longDf, shortDf, on='date', how='inner')

    result[long] = result[["close_x"]]
    result[short] = result[["close_y"]]

    result = result.drop(columns=['close_x', 'close_y'])

    return result


# 策略实现
def strategy(df):
    # 回测策略：BTC 定投
    df["invest"] = invest
    df["当天买入多头"] = df[[long]].apply(lambda x: invest / x[long], axis=1)
    df["当天买入空头"] = df[[short]].apply(lambda x: invest / x[short], axis=1)

    df["累计多头"] = df["当天买入多头"].cumsum()
    df["累计空头"] = df["当天买入空头"].cumsum()

    df["多头成本"] = df["invest"].cumsum()
    df["空头收入"] = df["invest"].cumsum()

    df["当前多头价值"] = df[long] * df["累计多头"]
    df["当前空头价值"] = df[short] * df["累计空头"]

    # 计算多头的盈利
    df["多头盈利"] = df["当前多头价值"] - df["多头成本"]
    # 计算空头的盈利
    df["空头盈利"] = df["空头收入"] - df["当前空头价值"]

    df["totalInvest"] = df["invest"].cumsum() * 2

    df["balance"] = df["空头盈利"] + df["多头盈利"] + df["totalInvest"]

    df['revenue'] = df["空头盈利"] + df["多头盈利"]
    df["revenueRate"] = df[["revenue", "totalInvest"]].apply(lambda x: x["revenue"] / x["totalInvest"], axis=1)

    df["date"] = pd.to_datetime(df["date"]).dt.date


def main():
    # 读取数据
    df = read_data()
    # 策略逻辑
    strategy(df)
    # 策略分析
    analyze_strategy(df)
    # 资金曲线
    df.plot('date', y=['revenue'])
    plt.show()


main()
