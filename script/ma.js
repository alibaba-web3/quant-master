const pro = require("ccxt").pro;
const {requestMethod, exchange} = require("./function");


async function main() {
    const exchangePro = new pro.binance({newUpdates: false, fetchImplementation: requestMethod, defaultType: "future"});
    const symbol = "BTCUSDT";
    const limit = 5;
    // 上一根 k 线是否上涨
    let isLastCandleUp = false;
    const ma = 7;
    const spread = 0.001;
    const interval = "1h";

    let candles = await exchange.fetchOHLCV(symbol, interval, null, ma + 1);
    let closeArr = candles.map(candle => Number(candle[4]));
    // 去掉最后一个未闭合的 k 线
    closeArr.pop();
    // 计算均线
    const mean = closeArr.reduce((a, b) => a + b) / closeArr.length;
    let count = 0;

    while (true) {
        try {
            const orderbook = await exchangePro.watchOrderBook(symbol, limit, {});

            const ask = Number(orderbook['asks'][0]);
            const bid = Number(orderbook['bids'][0]);

            if (bid > mean) {
                console.log("bid > mean", bid, mean);
            } else if (bid < mean) {
                console.log("bid < mean", bid, mean);
            }

            if (count % 1000 === 0) {
                candles = await exchange.fetchOHLCV(symbol, interval, null, ma + 1);
            }

            count++;
        } catch (e) {
            console.log(e);
            break;
        }
    }
}

main();
