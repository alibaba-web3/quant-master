# 数据下载后放到 data 目录下
# 方式1: 页面下载
# https://alibaba-web3.vercel.app/dataset/download

# 方式2: 数据下载脚本
import ccxt
import pandas as pd
import os
import concurrent.futures

exchange = ccxt.binance({
    'rateLimit': 1200,  # Binance API rate limit
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
})


def save_binance_data(symbol, timeframe, to_path='./data/binance/1d'):
    # 检查目标文件夹是否存在
    if not os.path.exists(to_path):
        os.makedirs(to_path)

    # 检查历史数据文件是否存在
    to_path = os.path.join(to_path, f"{symbol.replace('/', '-')}-{timeframe}.csv")

    if os.path.isfile(to_path):
        # 如果文件存在，则加载已有数据
        local_df = pd.read_csv(to_path, index_col='timestamp', parse_dates=True)
        # 获取已有数据的最后时间戳，并更新起始时间
        last_timestamp = int(local_df.index[-1].timestamp() * 1000)
        start_time = last_timestamp + 1

        bars = fetch_all_ohlcv(symbol, timeframe, start_time)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 没有新数据，直接返回
        if df.empty:
            print(f"{symbol} no new data")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        # 合并本地数据和新获取的数据
        df = pd.concat([local_df, df])

        df.to_csv(to_path)
        print(f"{symbol} data saved to {to_path}")
    else:
        bars = fetch_all_ohlcv(symbol, timeframe)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        df.to_csv(to_path)
        print(f"{symbol} data saved to {to_path}")


def download_all_binance_data(timeframe, to_path='./data/binance/'):
    exchange.load_markets()

    # 只保留永续合约

    symbols = [symbol.replace(":USDT", "") for symbol in exchange.symbols if ':USDT' in symbol and "-" not in symbol]

    print(symbols)

    # 检查目标文件夹是否存在
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    to_path = os.path.join(to_path, timeframe)
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    to_path = os.path.abspath(to_path)

    # 单线程下载
    # for index, symbol in enumerate(symbols):
    #     print(f"Current iteration: {index + 1}/{len(symbols)}")
    #
    #     save_binance_data(symbol, timeframe, to_path=to_path)

    # 多线程下载
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(save_binance_data, symbol, timeframe, to_path=to_path): symbol for symbol in symbols}

        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                print(f"Completed download for {symbol}")
            except Exception as exc:
                print(f"Generated an exception for {symbol}: {exc}")


def fetch_all_ohlcv(symbol, timeframe, start_time=1514764800000):
    # 2018年1月1日 00:00:00的时间戳（毫秒）

    # 初始化空的DataFrame
    df = pd.DataFrame()
    limit = 1000
    # 循环获取K线数据
    while True:
        # 获取K线数据
        klines = exchange.fetch_ohlcv(symbol, timeframe, since=start_time, limit=limit)

        # 如果没有获取到数据，则退出循环
        if len(klines) == 0:
            return df

        start_time = klines[-1][0] + 1

        # 转换为DataFrame格式
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms')
        print("获取 {} k 线数据，时间段：{} - {}".format(symbol, klines_df['timestamp'].iloc[0],
                                                       klines_df['timestamp'].iloc[-1]))

        # 将数据添加到总的DataFrame中
        df = pd.concat([df, klines_df])

        if len(klines) < limit:
            return df


if __name__ == "__main__":
    download_all_binance_data('4h')
