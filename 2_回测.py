import os

import matplotlib.pyplot as plt
import pandas as pd

# 示例策略：BTC 定投

# 每天定投金额
invest = 100

# 返回当前文件路径
root_path = os.path.abspath(os.path.dirname(__file__))

# 读取所有现货数据
path = root_path + '/data/spot.csv'
df = pd.read_csv(path, encoding='utf-8', skiprows=0)

# 删除不需要的数据
df.drop(
    columns=['buying_turnover', 'buying_volume', 'close_time', 'trading_volume', 'turnover', 'volume', 'source', 'id'],
    inplace=True)

# 只保留 BTC 数据
df = df[df['symbol'] == "BTCUSDT"]

df["当天投资"] = invest
df["当天买入BTC"] = df[["open"]].apply(lambda x: invest / x["open"], axis=1)
df["累计BTC"] = df["当天买入BTC"].cumsum()
df["累计投资"] = df["当天投资"].cumsum()
df["balance"] = df[["累计BTC", "close"]].apply(lambda x: x["累计BTC"] * x["close"], axis=1)
df['revenue'] = df[["balance", "累计投资"]].apply(lambda x: x["balance"] - x["累计投资"], axis=1)
df["revenueRate"] = df[["revenue", "累计投资"]].apply(lambda x: x["revenue"] / x["累计投资"], axis=1)
df["open_time"] = pd.to_datetime(df["open_time"])

# 资金曲线
df.plot('open_time', y=['revenueRate'])
plt.show()
