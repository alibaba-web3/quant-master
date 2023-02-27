import os

import matplotlib.pyplot as plt
import pandas as pd

# 示例策略：TVL 相比昨天上升则买入并持有 1 天

# 每次投入金额
invest = 100
symbol = "MKR"

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
df = pd.merge(spotDf, tvlDf, on=["date", "symbol"])

# 回测策略：TVL 相比昨天上升则买入并持有 1 天
df["tvl变化"] = df["tvl"] - df["tvl"].shift(-1)
df.dropna(axis=0, how='any', inplace=True)
# df["当天投资"] = df[["tvl变化"]].apply(lambda x: 100 if x > 0 else 0)

df.loc[df['tvl变化'] <= 0, '当天投资'] = 0
df.loc[df['tvl变化'] > 0, '当天投资'] = 100

df.loc[df['当天投资'] > 0, '本次盈亏'] = (df["close"].shift(1) - df["close"]) / df["close"]

df["累计投资"] = df["当天投资"].cumsum()
df["totalRevenue"] = df["本次盈亏"].cumsum()

# 补充空缺的数据
df["totalRevenue"] = df["totalRevenue"].fillna(method='pad')

# 资金曲线
df.plot('date', y=['totalRevenue'])
plt.show()
