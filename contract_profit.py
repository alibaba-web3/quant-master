import os

import matplotlib.pyplot as plt
import pandas as pd

# 示例策略：协议手续费 上升时买入并持有 1 天

# 每次投入金额
invest = 100
symbol = "UNI"
# 手续费
fee = 0.0004

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
# profitDf.drop(columns=['contract_address', 'time'], inplace=True)

# 合约调用数据和价格数据整理
df = pd.merge(spotDf, profitDf, on=["date", "symbol"])

# 回测策略：协议手续费 上升时买入并持有 1 天
df["feeUp"] = df["total_fees"] - df["total_fees"].shift(-1)
df.dropna(axis=0, how='any', inplace=True)
df["当天投资"] = df[["feeUp"]].iloc[:, 0].apply(lambda x: 100 if x > 0 else 0)

df.loc[df['feeUp'] >= 0, '当天投资'] = 100
df.loc[df['feeUp'] < 0, '当天投资'] = 0

df.loc[df['当天投资'] > 0, '本次盈亏'] = (df["close"].shift(-1) - df["close"]) / df["close"] - fee * 2

df["累计投资"] = df["当天投资"].cumsum()
df["totalRevenue"] = df["本次盈亏"].cumsum()

# 补充空缺的数据
df["totalRevenue"] = df["totalRevenue"].fillna(method='pad')

# 资金曲线
df.plot('date', y=['totalRevenue'])
plt.show()
