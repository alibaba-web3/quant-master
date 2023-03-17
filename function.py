def analyze_strategy(df):
    # 计算最大回撤
    df['maxRevenueRate'] = df['revenueRate'].cummax()
    df['drawdown'] = df['revenueRate'] - df['maxRevenueRate']
    max_drawdown = df['drawdown'].min()

    # 计算策略年化收益率
    hold_date = df["date"].tail(1).iloc[0] - df["date"].head(1).iloc[0]
    hold_days = hold_date.days
    hold_year = hold_days / 365
    revenue_rate = df["revenueRate"].iloc[-1] * 100 / hold_year

    print("策略年化收益率：", revenue_rate, "%", "最大回撤：", max_drawdown, "%")
