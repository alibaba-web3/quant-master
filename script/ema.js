const SMA = require('technicalindicators').SMA;
const {
    exchange,
    sleep,
    createBestLimitBuyOrderUntilFilled,
    createBestLimitSellOrderUntilFilled
} = require("./function.js");

// 下单金额
let invest = 100;
// 短均线周期
let smaShortPeriod = 5;
// 长均线周期
let smaLongPeriod = 20;
let symbol = 'BTC/USDT';

// exchange.fetchTickers().then(async markets => {
//     console.log(markets);
// });

/**
 * 查询收盘 k 线价格
 * @returns {Promise<number[]>}
 */
async function fetchOHLCV() {
    let ohlcv = await exchange.fetchOHLCV(symbol, '1d');
    // 收盘价
    return ohlcv.map(x => x[4]);
}

/**
 * 计算双均线
 */
async function calculateSMA(closePrices) {
    let smaShort = SMA.calculate({period: smaShortPeriod, values: closePrices});
    let smaLong = SMA.calculate({period: smaLongPeriod, values: closePrices});

    return {
        smaShort: smaShort,
        smaLong: smaLong
    };
}

async function ema() {

    let closePrices = await fetchOHLCV();
    let {smaShort, smaLong} = await calculateSMA(closePrices);

    let lastSmaShort = smaShort[smaShort.length - 1];
    let lastSmaLong = smaLong[smaLong.length - 1];

    let positions = await exchange.fetchPositions();
    positions = positions.filter(x => x.notional !== 0);
    if (lastSmaShort > lastSmaLong) {
        console.log(`${symbol} 短均线大于长均线，做多`);

        let position = positions.find(x => x.symbol === symbol);

        if (position && position.notional > 0) {
            console.log(`${symbol} 已有仓位，不再做多`);
        } else if (position && position.notional < 0) {
            console.log(`${symbol} 已有仓位，平仓`);
            await createBestLimitSellOrderUntilFilled(symbol, invest);
            await createBestLimitBuyOrderUntilFilled(symbol, invest);
        } else {
            await createBestLimitBuyOrderUntilFilled(symbol, invest);
        }

    } else if (lastSmaShort < lastSmaLong) {
        console.log(`${symbol} 短均线小于长均线，做空`);
        let position = positions.find(x => x.symbol === symbol);

        if (position && position.notional < 0) {
            console.log(`${symbol} 已有仓位，不再做空`);

        } else if (position && position.notional > 0) {
            console.log(`${symbol} 已有仓位，平仓`);
            await createBestLimitBuyOrderUntilFilled(symbol, invest);
            await createBestLimitSellOrderUntilFilled(symbol, invest);
        } else {
            await createBestLimitSellOrderUntilFilled(symbol, invest);
        }
    } else {
        console.log('Nothing to do...');
    }
}

async function main() {

    // 加载市场
    await exchange.loadMarkets();

    while (true) {
        console.log("start");
        await ema();
        // 每天执行一次
        await sleep(1000 * 60 * 60 * 24);

        // 测试使用
        // await sleep(1000);
    }
}

main();

