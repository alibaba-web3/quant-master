const config = require("./config.json");
const HttpsProxyAgent = require("https-proxy-agent");
const fetch = require("node-fetch");
const exchangeInfo = require("./binanceExchangeInfo.json");

// 官方文档：https://github.com/ccxt/ccxt
const ccxt = require("ccxt");

// 代理服务
const agent = new HttpsProxyAgent(config.proxy);

const requestMethod = function (url, options) {
    if (config.env === "local") {
        return fetch(url, Object.assign({}, options, {agent: agent}));
    } else {
        return fetch(url, Object.assign({}, options));
    }
};

let exchangeClass = ccxt["binance"];
let exchange = new exchangeClass({
    apiKey: config.apiKey,
    secret: config.apiSecret,
    fetchImplementation: requestMethod,
    enableRateLimit: true,
    options: {defaultType: "future"},
});

/**
 * 市价下单
 *
 * @param symbol 交易对
 * @param amount 买入数量
 */
function createMarketBuyOrder(symbol, amount) {
    // 调用 `createOrder` 方法下单
    exchange.createOrder(symbol, 'market', 'buy', amount).then((order) => {
        console.log(order); // 输出订单信息
    }).catch((error) => {
        console.error(error);
    });
}

async function createBestLimitSellOrder(symbol, invest) {
    let quantityPrecision = getQuantityPrecision(symbol);
    let pricePrecision = getPricePrecision(symbol);

    let price = await getBestPrice(symbol);

    let amount = (invest / price).toFixed(quantityPrecision);

    return await createLimitSellOrder(symbol, amount, price.toFixed(pricePrecision), "future");
}

async function createBestLimitBuyOrder(symbol, invest) {
    let quantityPrecision = getQuantityPrecision(symbol);
    let pricePrecision = getPricePrecision(symbol);

    let price = await getBestPrice(symbol);

    let amount = (invest / price).toFixed(quantityPrecision);

    return await createLimitBuyOrder(symbol, amount, price.toFixed(pricePrecision), "future");
}

/**
 * 获取最优价格
 * @param symbol
 * @returns {Promise<number>}
 */
async function getBestPrice(symbol) {
    let ticker = await exchange.fapiPublicGetTickerBookTicker({symbol});

    let ask = Number(ticker.askPrice);
    let bid = Number(ticker.bidPrice);
    return (ask + bid) / 2;
}

function getQuantityPrecision(symbol) {
    let exchangeInfo = fetchFutureExchangeInfo();

    return Number(exchangeInfo.symbols.find((coin) => {
        return coin.symbol.toLowerCase() === symbol.toLowerCase();
    }).quantityPrecision);
}

function getPricePrecision(symbol) {
    let exchangeInfo = fetchFutureExchangeInfo();

    return Number(exchangeInfo.symbols.find((coin) => {
        return coin.symbol === symbol;
    }).pricePrecision);
}

function fetchFutureExchangeInfo() {
    return exchangeInfo;
    // return gridAccount.fapiPublicGetExchangeInfo();
}

async function createLimitBuyOrder(symbol, amount, price, type) {
    return exchange.createLimitBuyOrder(symbol, amount, price, {
        type,
    });
}

async function createLimitSellOrder(symbol, amount, price, type) {
    return exchange.createLimitSellOrder(symbol, amount, price, {
        type,
    });
}

module.exports = {exchange, createBestLimitSellOrder, createBestLimitBuyOrder};
