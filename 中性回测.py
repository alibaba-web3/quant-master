import os

import matplotlib.pyplot as plt
import pandas as pd

from function import *

# 每天定投金额
invest = 100
timeframe = "1h"
fee = 0.0004 + 0.0001
ma = 300
long = "AXS-USDT"
short = "SLP-USDT"

start_date = '2021-01-01'
end_date = '2024-01-01'

root_path = os.path.abspath(os.path.dirname(__file__))
ohlcv_dir_path = root_path + '/data/binance/' + timeframe + '/'


def compute_rsi(series, window=14):
    # 1. 计算价格变化
    delta = series.diff()

    # 2. 将正的价格变化和负的价格变化分开
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    # 3. 计算平均值
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # 4. 计算相对强度（RS）
    rs = avg_gain / avg_loss

    # 5. 使用RS计算RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi


# 读取整理数据
def read_data(long, short):
    # 返回当前文件路径
    root_path = os.path.abspath(os.path.dirname(__file__))

    # 读取所有现货数据
    longPath = ohlcv_dir_path + long + '-' + timeframe + '.csv'
    longDf = pd.read_csv(longPath, encoding='utf-8', skiprows=0)
    shortPath = ohlcv_dir_path + short + '-' + timeframe + '.csv'
    shortDf = pd.read_csv(shortPath, encoding='utf-8', skiprows=0)

    # 删除不需要的数据
    longDf.drop(
        columns=['volume'],
        inplace=True)
    shortDf.drop(
        columns=['volume'],
        inplace=True)

    # longDf = df[df['symbol'] == long]
    # shortDf = df[df['symbol'] == short]
    # 按照时间合并数据
    result = pd.merge(longDf, shortDf, on='timestamp', how='inner')

    result['rate'] = result['open_x'] / result['open_y']
    # result.drop(columns=['open_x', 'open_y', 'low_x', 'low_y', 'close_x', 'close_y', 'symbol_x'])

    result["date"] = pd.to_datetime(result["timestamp"]).dt.date
    # 选择时间范围
    result = result[(result['date'] >= pd.to_datetime(start_date)) & (result['date'] <= pd.to_datetime(end_date))]

    return result


# 策略实现
def strategy(df):
    df["signal"] = 0
    # # 价格比例
    # df["rate"] = df["open_x"] / df["open_y"]
    # 价格比例的均线
    df["rate_ma"] = df["rate"].rolling(ma).mean()

    # 均线开仓信号
    # df.loc[df["rate"] > df["rate_ma"], "signal"] = 1
    # df.loc[df["rate"] < df["rate_ma"], "signal"] = -1

    # # 布林带计算
    df['upper'] = df['rate_ma'] + 2 * df['rate'].rolling(ma).std()
    df['lower'] = df['rate_ma'] - 2 * df['rate'].rolling(ma).std()
    # # 布林带开仓信号
    #

    df.loc[df["rate"] > df["upper"], "signal"] = -1
    df.loc[df["rate"] < df["lower"], "signal"] = 1
    df.loc[df["rate"] == df["lower"], "signal"] = 0

    # 投入金额
    df.loc[df["signal"] != 0, "invest"] = 100
    df.loc[df["signal"] == 0, "invest"] = 0

    # RSI计算
    # df['RSI'] = compute_rsi(df['rate'])

    # RSI开仓信号
    # df['signal'] = 0
    # df.loc[df["RSI"] >= 55, "signal"] = -1
    # df.loc[df["RSI"] <= 45, "signal"] = 1

    # 根据均线开仓信号计算仓位
    # df['daily_return'] = df['rate'].pct_change()

    # 计算策略收益
    # df['strategy_return'] = df['signal'].shift() * df['daily_return']

    # 做多部分收益计算
    df['long_return'] = df['open_x'].pct_change()
    # 做空部分收益计算
    df['short_return'] = df['open_y'].pct_change()
    # 整体收益
    # df['strategy_return'] = df['signal'].shift() * (df['long_return'] - df['short_return']) / 2
    # 只做多
    # df['strategy_return'] = df['signal'].shift() * df['long_return']
    # 只做空
    df['strategy_return'] = df['signal'].shift() * -df['short_return']

    # 计算手续费
    df['fee'] = 0
    df.loc[df['signal'] * df['signal'].shift() == -1, 'fee'] = fee * 4
    df.loc[df['signal'] * df['signal'].shift() == 1, 'fee'] = 0
    df['fee'] = np.where((df['signal'] * df['signal'].shift() == 0) & (df['signal'] == 0) & (df['signal'].shift() != 0),
                         fee * 2, df['fee'])

    df['strategy_return'] = df['strategy_return'] - df['fee']

    # 计算累计收益
    df['cumulative_strategy_returns'] = np.cumsum(df['strategy_return'])
    df['cumulative_fee'] = np.cumsum(df['fee'])

    df["revenueRate"] = df['cumulative_strategy_returns']


def main(long, short):
    # 读取数据
    df = read_data(long, short)
    # 策略逻辑
    strategy(df)
    # 策略分析
    revenue_rate, sharpe_ratio = analyze_strategy(df)
    # 资金曲线
    df.plot('date', y=['revenueRate'])
    plt.show()
    # if sharpe_ratio > 0:
    #     print(f"{long} {short} 最终收益率：{format(revenue_rate, '.3f')}")


main(long, short)
symbols = []
for root, dirs, files in os.walk(ohlcv_dir_path):
    for file in files:
        if file.endswith(".csv"):
            symbol = file.split("-" + timeframe)[0]
            symbols.append(symbol)

# 回测所有的币
# for long in symbols:
#     for short in symbols:
#         if long != short:
#             main(long, short)
