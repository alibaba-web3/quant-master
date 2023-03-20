import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from scipy.stats.mstats import gmean
from datetime import datetime
from function import *

'''
数据清洗
'''
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
df["date"] = pd.to_datetime(df["openTime"])


'''
计算ahr999
'''
# 200日定投成本，几何平均
df['200_cost'] = df['close'].rolling(200, min_periods=200).apply(gmean, raw=True)

# 指数增长估计
# 拟合币价 y = 10^(5.84log(币龄)-17.01)
df['10_base'] = 10
df['btc_day_age'] = df['date'].apply(lambda x: (x - datetime(2009, 1, 3)).days)
df['btc_estimate'] = df['10_base'].pow(5.84 * df['btc_day_age'].apply(np.log10) - 17.01)
df['ahr999'] = df[['close', '200_cost', 'btc_estimate']] \
    .apply(lambda x: x['close'] / x['200_cost'] * x['close'] / x['btc_estimate'], axis=1)


'''
BTC定投策略
'''
# 每天定投基数
base_invest = 100


# 自定义因子函数, 用坐标 (0.45, 2), (1.2, 1) 拟合的二次函数：
def get_factor(index):
    # ahr999 大于 1.2 就不投了
    if index > 1.2:
        return 0
    return index*index - 2.983 * index + 3.14


df["当天投资"] = df['ahr999'].apply(lambda x: base_invest * get_factor(x))
df["当天买入BTC"] = df[["当天投资", "open"]].apply(lambda x: x["当天投资"] / x["open"], axis=1)
df["累计BTC"] = df["当天买入BTC"].cumsum()
df["累计投资"] = df["当天投资"].cumsum()
df["balance"] = df[["累计BTC", "close"]].apply(lambda x: x["累计BTC"] * x["close"], axis=1)
df['revenue'] = df[["balance", "累计投资"]].apply(lambda x: x["balance"] - x["累计投资"], axis=1)
df["revenueRate"] = df[["revenue", "累计投资"]].apply(lambda x: x["revenue"] / x["累计投资"], axis=1)


# 策略分析
analyze_strategy(df)

'''
画图
'''
# 资金曲线
df.plot('date', y=['revenueRate'])
plt.show()
