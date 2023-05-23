const config = require("./config.json");
const HttpsProxyAgent = require("https-proxy-agent");
const fetch = require("node-fetch");

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

let exchange = new ccxt["binance"]({
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

// 下单做多最优限价订单
async function createBestLimitBuyOrder(symbol, invest) {
    let price = await getBestPrice(symbol);
    let amount = invest / price;

    return await createLimitBuyOrder(symbol, exchange.amountToPrecision(symbol, amount), exchange.priceToPrecision(symbol, price));
}

// 下单做空最优限价订单
async function createBestLimitSellOrder(symbol, invest) {
    let price = await getBestPrice(symbol);
    let amount = invest / price;

    return await createLimitSellOrder(symbol, exchange.amountToPrecision(symbol, amount), exchange.priceToPrecision(symbol, price));
}

/**
 * 按数量下单最佳限价空单下单
 *
 * @param symbol 交易对
 * @param amount 数量
 */
async function createBestLimitSellOrderByAmount(symbol, amount) {
    let price = await getBestPrice(symbol);

    return await createLimitSellOrder(symbol, exchange.amountToPrecision(symbol, amount), exchange.priceToPrecision(symbol, price));
}

/**
 * 按数量下单最佳下架限价多单下单
 */
async function createBestLimitBuyOrderByAmount(symbol, amount) {
    let price = await getBestPrice(symbol);

    return await createLimitBuyOrder(symbol, exchange.amountToPrecision(symbol, amount), exchange.priceToPrecision(symbol, price));
}

/**
 * 获取最优价格
 * @param symbol
 * @returns {Promise<number>}
 */
async function getBestPrice(symbol) {
    let ticker = await exchange.fetchOrderBook(symbol, 5);

    let bid = ticker.bids[0][0];
    let ask = ticker.asks[0][0];
    return (ask + bid) / 2;
}

/**
 * 限价买单
 */
async function createLimitBuyOrder(symbol, amount, price) {
    console.log(`${symbol} 做多下单, 价格: ${price} , 数量: ${amount}`);
    try {
        return await exchange.createLimitBuyOrder(symbol, amount, price);
    } catch (error) {
        if (error instanceof ccxt.ExchangeNotAvailable) {
            await sleep(1000);
            try {
                // 重试
                return await exchange.createLimitBuyOrder(symbol, amount, price);
            } catch (e) {
                if (e instanceof ccxt.ExchangeNotAvailable) {
                    await sleep(1000);
                    // 二次重试
                    return await exchange.createLimitBuyOrder(symbol, amount, price);
                } else {
                    console.error('Error createLimitBuyOrder second:', e);
                    throw e;
                }
            }
        } else {
            console.error('Error createLimitBuyOrder:', error);
            throw error;
        }
    }

}

// 限价卖单
async function createLimitSellOrder(symbol, amount, price) {
    console.log(`${symbol} 做空下单, 价格: ${price} , 数量: ${amount}`);
    try {
        return await exchange.createLimitSellOrder(symbol, amount, price);
    } catch (error) {
        if (error instanceof ccxt.ExchangeNotAvailable) {
            await sleep(1000);
            try {
                // 重试
                return await exchange.createLimitSellOrder(symbol, amount, price);
            } catch (e) {
                if (e instanceof ccxt.ExchangeNotAvailable) {
                    await sleep(1000);
                    // 二次重试
                    return await exchange.createLimitSellOrder(symbol, amount, price);
                } else {
                    console.error('Error createLimitSellOrder second:', e);
                    throw e;
                }
            }
        } else {
            console.error('Error createLimitSellOrder:', error);
            throw error;
        }
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 最佳买单直到成交
async function createBestLimitBuyOrderUntilFilled(symbol, invest) {
    let order = await createBestLimitBuyOrder(symbol, invest);

    return await checkBuyOrder(order);
}

// 按照数量下单最佳买单直到成交
async function createBestLimitBuyOrderByAmountUntilFilled(symbol, amount) {
    let order = await createBestLimitBuyOrderByAmount(symbol, amount);

    return await checkBuyOrder(order);
}

async function checkBuyOrder(order) {
    let num = 0;
    let maxNum = 10;

    let intervalId = setInterval(async () => {
        num++;
        order = await exchange.fetchOrder(order.id, order.symbol);

        console.log(`做多 ${order.symbol} 检查订单 ${order.id} 是否成交`, num);

        if (order.status === "closed") {
            console.log(`做多 ${order.symbol} 订单 ${order.id} 已成交`);
            clearInterval(intervalId);
        }

        if (num > maxNum) {
            console.log(`做多 ${order.symbol} 订单 ${order.id} 未完全成交，取消后重新下单`);
            await cancelOrder(order.symbol, order.id);
            order = await createBestLimitBuyOrderByAmount(order.symbol, order.remaining);
            num = 0;
        }
    }, 10 * 1000);

    return order;
}

// 最佳卖单直到成交
async function createBestLimitSellOrderUntilFilled(symbol, invest) {
    let order = await createBestLimitSellOrder(symbol, invest);

    return await checkSellOrder(order);
}

// 按照数量下单最佳卖单直到成交
async function createBestLimitSellOrderByAmountUntilFilled(symbol, amount) {
    let order = await createBestLimitSellOrderByAmount(symbol, amount);

    return await checkSellOrder(order);
}

async function checkSellOrder(order) {
    let num = 0;
    let maxNum = 10;
    let symbol = order.symbol;

    let intervalId = setInterval(async () => {
        num++;
        order = await exchange.fetchOrder(order.id, order.symbol);

        console.log(`做空 ${order.symbol} 检查订单 ${order.id} 是否成交`, num);

        if (order.status === "closed") {
            console.log(`做空 ${order.symbol} 订单 ${order.id} 已成交`);
            clearInterval(intervalId);
        }

        if (num > maxNum) {
            console.log(`做空 ${order.symbol} 订单 ${order.id} 未完全成交，取消后重新下单`);
            await cancelOrder(symbol, order.id);
            order = await createBestLimitSellOrderByAmount(symbol, order.remaining);
            num = 0;
        }
    }, 10 * 1000);

    return order;
}

/**
 * 取消订单
 * @param symbol 交易对
 * @param orderId 订单id
 */
async function cancelOrder(symbol, orderId) {
    console.log(`取消 ${symbol} 订单 ${orderId}`);
    return exchange.cancelOrder(orderId, symbol);
}

module.exports = {
    sleep,
    exchange,
    createBestLimitSellOrderUntilFilled,
    createBestLimitBuyOrder,
    createMarketBuyOrder,
    createBestLimitBuyOrderUntilFilled,
    createBestLimitBuyOrderByAmount,
    createBestLimitBuyOrderByAmountUntilFilled,
    createBestLimitSellOrderByAmountUntilFilled,
    getBestPrice
};
