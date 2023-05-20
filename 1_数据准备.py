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
    'options': {'defaultType': 'future'},
})

def save_binance_data(symbol, timeframe, since=None, to_path='./data/binance/1d'):
    if not os.path.exists(to_path):
        os.makedirs(to_path)

    bars = fetch_all_ohlcv(symbol, timeframe)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    output_path = os.path.join(to_path, f"{symbol.replace('/', '-')}-{timeframe}.csv")
    df.to_csv(output_path)
    print(f"{symbol} data saved to {output_path}")


def download_all_binance_data(timeframe, to_path='./data/binance/'):
    markets = exchange.load_markets()
    symbols = [symbol for symbol in markets if
               markets[symbol]['info']['quoteAsset'] == 'USDT' and markets[symbol]['info']['contractType'] == 'PERPETUAL']

    to_path = os.path.join(to_path, timeframe)
    for index, symbol in enumerate(symbols):
        print(f"Current iteration: {index + 1}/{len(symbols)}")
        save_binance_data(symbol, timeframe, to_path=to_path)


def fetch_all_ohlcv(symbol, timeframe):
    start_time = 1514764800000  # 2018年1月1日 00:00:00的时间戳（毫秒）

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

        # 转换为DataFrame格式
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms')

        # 将数据添加到总的DataFrame中
        df = pd.concat([df, klines_df])

        if len(klines) < limit:
            return df

        return df


if __name__ == "__main__":
    download_all_binance_data('1h')
