import os

import matplotlib.pyplot as plt
import pandas as pd

from function import *

# 每天定投金额
invest = 100
timeframe = "1h"
fee = 0.0004 + 0.00025
ma = 50
# long = "LUNA2-USDT"
# short = "1000LUNC-USDT"
long = "CRV-USDT"
short = "CVX-USDT"

start_date = '2023-09-01'
end_date = '2023-10-01'

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

    result["date"] = pd.to_datetime(result["timestamp"]).dt.to_pydatetime()

    return result


# 策略实现
def strategy(df, ma):
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
    df['middle'] = df['rate_ma']

    # 布林带开仓信号
    df.loc[df["rate"] > df["upper"], "signal"] = -1
    df.loc[df["rate"] < df["lower"], "signal"] = 1
    df.loc[df["rate"] == df["lower"], "signal"] = 0

    # # 价格比例往上穿然后回到均线
    # df.loc[(df["rate"].shift() < df["upper"].shift()) & (df["rate"] > df["upper"]), "signal"] = -1
    # df.loc[(df["rate"].shift() > df["middle"].shift()) & (df["rate"] < df["middle"]), "signal"] = 0
    #
    # # 获取所有-1信号的位置
    # short_positions = df[df["signal"] == -1].index.tolist()
    #
    # # 获取所有0信号的位置
    # close_positions = df[df["signal"] == 0].index.tolist()
    #
    # # 对于每个-1信号，找到其后的第一个0信号，并将它们之间的所有值都设置为-1
    # for short_position in short_positions:
    #     # 找到大于当前-1信号位置的第一个0信号位置
    #     close_position = next((x for x in close_positions if x > short_position), None)
    #
    #     # 如果找到了0信号位置，则将它们之间的所有值都设置为-1
    #     if close_position:
    #         df.loc[short_position:close_position, "signal"] = -1

    # 投入金额
    df["invest"] = 0
    df.loc[df["signal"] == -1, "invest"] = 100
    df.loc[df["signal"] == 1, "invest"] = 100

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
    df['strategy_return'] = df['signal'].shift() * (df['long_return'] - df['short_return']) / 2
    # 只做币1
    # df['strategy_return'] = df['signal'].shift() * df['long_return']
    # 只做币2
    # df['strategy_return'] = df['signal'].shift() * -df['short_return']

    # 只做多
    # df.loc[df["signal"].shift() == 1, "strategy_return"] = df['long_return']
    # df.loc[df["signal"].shift() == -1, "strategy_return"] = df['short_return']
    # df['strategy_return'] = df['strategy_return'].fillna(0)

    # 只做空
    # df.loc[df["signal"].shift() == 1, "strategy_return"] = -df['short_return']
    # df.loc[df["signal"].shift() == -1, "strategy_return"] = -df['long_return']
    # df['strategy_return'] = df['strategy_return'].fillna(0)

    # 计算手续费
    df['fee'] = 0
    df.loc[df['signal'] * df['signal'].shift() == -1, 'fee'] = fee * 4
    df.loc[df['signal'] * df['signal'].shift() == 1, 'fee'] = 0
    df['fee'] = np.where((df['signal'] * df['signal'].shift() == 0) & (df['signal'] == 0) & (df['signal'].shift() != 0),
                         fee * 2, df['fee'])

    df['strategy_return'] = df['strategy_return'] - df['fee']

    # 选择时间范围
    df = df[df['date'] >= pd.to_datetime(start_date)]
    df = df[df['date'] <= pd.to_datetime(end_date)]

    # 计算累计收益
    df['cumulative_strategy_returns'] = np.cumsum(df['strategy_return'])
    df['cumulative_fee'] = np.cumsum(df['fee'])

    df["revenueRate"] = df['cumulative_strategy_returns']
    df["balance"] = df['cumulative_strategy_returns'] * 100 + 100
    return df

def main(long, short, ma):
    # 读取数据
    df = read_data(long, short)
    # 策略逻辑
    df = strategy(df, ma)
    # 策略分析
    revenue_rate, max_drawdown, profit_loss_ratio, winRate = analyze_strategy(df)
    # 资金曲线
    # df.plot('date', y=['revenueRate'])
    # plt.show()
    # if sharpe_ratio > 0:
    print(
        f"{long} {short} {ma} 年化收益率：{format(revenue_rate, '.3f')} 最大回撤：{format(max_drawdown, '.3f')} 盈亏比：{format(profit_loss_ratio, '.3f')} 胜率：{format(winRate * 100, '.1f')}%")
    df = df[['date', 'revenueRate', 'invest', 'fee', 'balance']]
    return df


# main(long, short, ma)
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

def test_all_param():
    # 遍历参数
    dfList = []
    for i in range(10, 1000, 10):
        df = main(long, short, i)
        dfList.append(df)
    df_combined = pd.concat(dfList)
    df_result = df_combined.groupby('date').sum().reset_index()
    df_result['leverage'] = df_result['invest'] / df_result['balance']
    max_invest = df_result['invest'].max()
    max_leverage = df_result['leverage'].max()

    emptyRate = df_result.loc[df_result['invest'] == 0, 'invest'].count() / df_result['invest'].count()
    totalFee = df_result['fee'].sum()
    print("空仓时间比例:", emptyRate, "最大杠杆:", max_leverage, "最大投入：", max_invest, "累计手续费: ",
          totalFee * invest)

    df_result.plot('date', y=['revenueRate'])
    plt.show()

test_all_param()
