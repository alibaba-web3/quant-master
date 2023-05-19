const ccxt = require('ccxt');
const SMA = require('technicalindicators').SMA;
const cron = require('node-cron');

const exchange = new ccxt.binance({
    apiKey: 'your_API_key',
    secret: 'your_API_secret'
});

let smaShortPeriod = 5;
let smaLongPeriod = 20;
let symbol = 'BTC/ETH';
let balance = {};

async function fetchOHLCV() {
    let ohlcv = await exchange.fetchOHLCV(symbol, '1d');
    let closePrices = ohlcv.map(x => x[4]); // Closing prices
    return closePrices;
}

async function calculateSMA(closePrices) {
    let smaShort = SMA.calculate({period : smaShortPeriod, values : closePrices});
    let smaLong = SMA.calculate({period : smaLongPeriod, values : closePrices});

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

async function main() {
    await updateBalance();

    let closePrices = await fetchOHLCV();
    let {smaShort, smaLong} = await calculateSMA(closePrices);

    let lastSmaShort = smaShort[smaShort.length - 1];
    let lastSmaLong = smaLong[smaLong.length - 1];

    if (lastSmaShort > lastSmaLong) {
        console.log('Placing buy order...');
        // Calculate amount based on your balance and strategy
        let amountToBuy = balance.free.BTC / 2;
        await placeOrder('buy', amountToBuy);
    } else if (lastSmaShort < lastSmaLong) {
        console.log('Placing sell order...');
        // Calculate amount based on your balance and strategy
        let amountToSell = balance.free.BTC;
        await placeOrder('sell', amountToSell);
    }
}

// Schedule the main function to run once a day at 00:00
cron.schedule('0 0 * * *', main);
