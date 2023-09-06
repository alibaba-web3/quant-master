import numpy as np


def analyze_strategy(df):
    # 计算最大回撤
    df['cumulative_max'] = df['revenueRate'].expanding().max()
    df['drawdown'] = (df['revenueRate'] - df['cumulative_max'])
    max_drawdown = df['drawdown'].min() * 100

    # 计算策略年化收益率
    hold_date = df["date"].tail(1).iloc[0] - df["date"].head(1).iloc[0]
    hold_days = hold_date.days
    hold_year = hold_days / 365
    revenue_rate = df["revenueRate"].iloc[-1] * 100 / hold_year

    # 计算胜率
    # df = df[df["invest"] != 0]
    df['dailyReturn'] = df['revenueRate'].diff()
    if df['dailyReturn'].count() != 0 & df.loc[df['dailyReturn'] != 0, 'dailyReturn'].count() != 0:
        df["winRate"] = df.loc[df['dailyReturn'] > 0, 'dailyReturn'].count() / df.loc[
            df['dailyReturn'] != 0, 'dailyReturn'].count()
    else:
        df["winRate"] = 0
    # 空仓时间比例
    df["emptyRate"] = df.loc[df['invest'] == 0, 'invest'].count() / df['invest'].count()

    # 夏普比率
    # avg_daily_return = df['dailyReturn'].mean()
    # daily_volatility = df['dailyReturn'].std()
    # sharpe_ratio = (avg_daily_return / daily_volatility) * np.sqrt(252)

    # 盈亏比
    if max_drawdown == 0:
        profit_loss_ratio = 0
    else:
        profit_loss_ratio = revenue_rate / -max_drawdown

    # print("策略评价：")
    # print("年化收益率：", format(revenue_rate, ".2f"), "%")
    # print("最大回撤：", format(max_drawdown, ".2f"), "%")
    # print("胜率：", format(df["winRate"].mean() * 100, ".2f"), "%")
    # print("盈亏比：", format(revenue_rate / -max_drawdown, ".2f"))
    # print("空仓时间比例：", format(df["emptyRate"].mean() * 100, ".2f"), "%")
    # print("夏普比率：", format(sharpe_ratio, ".2f"))
    return revenue_rate, max_drawdown, profit_loss_ratio, df["winRate"].mean()
