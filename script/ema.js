const SMA = require('technicalindicators').SMA;
const {exchange} = require("./function.js");

let smaShortPeriod = 5;
let smaLongPeriod = 20;
let symbol = 'BTC/USDT';
let balance = {};

async function fetchOHLCV() {
    let ohlcv = await exchange.fetchOHLCV(symbol, '1d');
    let closePrices = ohlcv.map(x => x[4]); // Closing prices
    return closePrices;
}

async function calculateSMA(closePrices) {
    let smaShort = SMA.calculate({period: smaShortPeriod, values: closePrices});
    let smaLong = SMA.calculate({period: smaLongPeriod, values: closePrices});

    return {
        smaShort: smaShort,
        smaLong: smaLong
    };
}

async function updateBalance() {
    balance = await exchange.fetchBalance();
}

async function placeOrder(type, amount) {
    let order = await exchange.createOrder(symbol, 'market', type, amount);
    return order;
}

async function ema() {
    await updateBalance();

    let closePrices = await fetchOHLCV();
    let {smaShort, smaLong} = await calculateSMA(closePrices);

    let lastSmaShort = smaShort[smaShort.length - 1];
    let lastSmaLong = smaLong[smaLong.length - 1];

    // TODO 如果有之前仓位，先平仓

    if (lastSmaShort > lastSmaLong) {
        console.log('Placing buy order...');
        // Calculate amount based on your balance and strategy
        let amountToBuy = balance.free.BTC / 2;
        // await placeOrder('buy', amountToBuy);
    } else if (lastSmaShort < lastSmaLong) {
        console.log('Placing sell order...');
        // Calculate amount based on your balance and strategy
        let amountToSell = balance.free.BTC;
        // await placeOrder('sell', amountToSell);
    } else {
        console.log('Nothing to do...');
    }
}

async function main() {
    while (true) {
        console.log("start");
        await ema();
        // 每天执行一次
        await new Promise(resolve => setTimeout(resolve, 1000 * 60 * 60 * 24));
    }

}

main();

