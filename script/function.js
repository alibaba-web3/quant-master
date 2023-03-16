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

let exchangeClass = ccxt["binance"];
let exchange = new exchangeClass({
    apiKey: config.apiKey,
    secret: config.apiSecret,
    fetchImplementation: requestMethod,
    enableRateLimit: true,
    // options: {defaultType: "future"},
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

module.exports = {exchange, createMarketBuyOrder};
