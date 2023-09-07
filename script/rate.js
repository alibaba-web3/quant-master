const pro = require("ccxt").pro;
const path = require("path");
const {requestMethod, exchange, sleep, readJson, saveJson, getMarkets, createLimitSellOrder} = require("./function");
const config = require("./config.json");
const moment = require("moment");
const technicalindicators = require('technicalindicators');

let exchangePro = new pro.binance({
    apiKey: config.apiKey,
    secret: config.apiSecret,
    newUpdates: false,
    fetchImplementation: requestMethod,
    defaultType: "future"
});

async function main() {

    const long = "CRV/USDT";
    const short = "CVX/USDT";

    const period = 50;
    const interval = "1h";

    let count = 0;

    let order = null;
    let closeOrder = null;
    const amount = 100;
    let initTargetShort1Price = 0;
    let targetShort1Price = 0;
    let targetCloseShort1Price = 0;

    try {
        let longTicker;
        let shortTicker;
        while (true) {

            if (order && order.status === "closed" && closeOrder && closeOrder.status === "closed") {
                console.log("交易周期结束");
                break;
            }

            try {
                const tickers = await exchangePro.watchTickers([long, short]);
                if (tickers[long]) {
                    longTicker = tickers[long];
                }
                if (tickers[short]) {
                    shortTicker = tickers[short];
                }

                if (!longTicker || !shortTicker) {
                    console.log(`${longTicker?.bid} ${shortTicker?.bid} tiker 数据为空`);
                    continue;
                }

                const longCandle = await exchange.fetchOHLCV(long, interval, null, period + 1);
                const shortCandle = await exchange.fetchOHLCV(short, interval, null, period + 1);

                const longCloseArr = longCandle.map(candle => Number(candle[4]));
                const shortCloseArr = shortCandle.map(candle => Number(candle[4]));
                const rateArr = longCloseArr.map((close, index) => close / shortCloseArr[index]);

                const bollingerbands = technicalindicators.bollingerbands({
                    period: period,
                    values: rateArr.slice(0, rateArr.length - 1),
                    stdDev: 2
                });
                const bolling = bollingerbands[bollingerbands.length - 1];
                const minRate = bolling.lower;
                const maxRate = bolling.upper;

                const currentRate = longTicker.bid / shortTicker.bid;
                console.log(`当前比率：${currentRate}，最小比率：${minRate}，最大比率：${maxRate}`);

                // 做空 币1 的目标价
                const newTargetShort1Price = maxRate * shortTicker.bid;
                if (targetShort1Price !== newTargetShort1Price) {
                    targetShort1Price = newTargetShort1Price;
                    if (order && order.status !== "closed") {
                        // 修改订单价格
                        await exchangePro.editOrder(order.id, order.symbol, "limit", "sell", amount, targetShort1Price);
                        console.log(`修改挂单 ${order.id} 价格为 ${targetShort1Price}`)
                    }
                }

                if (!order) {
                    // 初始下单
                    order = await createLimitSellOrder(long, amount, targetShort1Price);
                    console.log(`初始挂单，做空 ${order.symbol} 下单 ${order.id} 成功`)
                } else {
                    // 平仓价格计算
                    const newTargetCloseShort1Price = maxRate * shortTicker.bid;
                    if (targetCloseShort1Price !== newTargetCloseShort1Price) {
                        targetCloseShort1Price = newTargetCloseShort1Price;
                        if (closeOrder && closeOrder.status !== "closed") {
                            // 修改订单价格
                            closeOrder = await exchangePro.editOrder(closeOrder.id, closeOrder.symbol, "limit", "buy", amount, targetCloseShort1Price);
                            console.log(`修改平仓挂单 ${closeOrder.id} 价格为 ${targetCloseShort1Price}`)
                        }
                    }

                    // 平仓挂单
                    if (!closeOrder && order.status === "closed" && targetCloseShort1Price < Number(order.price)) {
                        closeOrder = await createLimitSellOrder(long, amount, targetShort1Price);
                        console.log(`平仓挂单，做空 ${closeOrder.symbol} 下单 ${closeOrder.id} 成功`)
                    }
                }

                count++;
                await sleep(200);
            } catch (e) {
                console.log(e);
                break;
            }
        }
    } catch (e) {
        console.error(e);
    } finally {
        await exchangePro.close();
    }
}


main();
