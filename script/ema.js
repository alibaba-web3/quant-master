const EMA = require('technicalindicators').EMA;
const {
    exchange,
    sleep,
    createBestLimitBuyOrderUntilFilled,
    createBestLimitSellOrderUntilFilled,
    ding,
    readConfig
} = require("./function.js");
const {createBestLimitSellOrderByAmountUntilFilled, createBestLimitBuyOrderByAmountUntilFilled} = require("./function");
const config = readConfig();
const emaConfig = config.ema;

// 下单金额
let invest = emaConfig.invest;
// 短均线周期
let emaShortPeriod = emaConfig.emaShortPeriod;
// 长均线周期
let emaLongPeriod = emaConfig.emaLongPeriod;
// k 线级别
let timeframe = emaConfig.timeframe;


/**
 * 查询收盘 k 线价格
 * @returns {Promise<number[]>}
 */
async function fetchOHLCV(symbol) {
    let ohlcv = await exchange.fetchOHLCV(symbol, timeframe);
    // 收盘价
    return ohlcv.map(x => x[4]);
}

/**
 * 计算双均线
 */
async function calculateEMA(closePrices) {
    let emaShort = EMA.calculate({period: emaShortPeriod, values: closePrices});
    let emaLong = EMA.calculate({period: emaLongPeriod, values: closePrices});

    return {
        emaShort: emaShort,
        emaLong: emaLong
    };
}

async function ema(symbol, trend = true) {

    let closePrices = await fetchOHLCV(symbol);
    let {emaShort, emaLong} = await calculateEMA(closePrices);

    let lastEmaShort = emaShort[emaShort.length - 1];
    let lastEmaLong = emaLong[emaLong.length - 1];
    console.log(`交易对 ${symbol} ${timeframe} 均线 ${emaShortPeriod} ${emaLongPeriod} 最新值 ${lastEmaShort} ${lastEmaLong}`);

    let positions = await exchange.fetchPositions();
    positions = positions.filter(x => x.notional !== 0);
    let position = positions.find(x => x.info.symbol === symbol);
    let longCondition;
    let shortCondition;
    if (trend) {
        // 趋势策略
        longCondition = lastEmaShort > lastEmaLong;
        shortCondition = lastEmaShort < lastEmaLong;
    } else {
        // 反转策略
        longCondition = lastEmaShort < lastEmaLong;
        shortCondition = lastEmaShort > lastEmaLong;
    }

    if (longCondition) {
        if (position && Number(position.info.positionAmt) > 0) {
            console.log(`${symbol} 已有仓位，不再做多`);
        } else if (position && Number(position.info.positionAmt) < 0) {
            console.log(`${symbol} 已有做空仓位，先平仓后做多`);
            let amount = Math.abs(position.info.positionAmt);
            await createBestLimitBuyOrderByAmountUntilFilled(symbol, amount);
            await createBestLimitBuyOrderUntilFilled(symbol, invest);
        } else {
            console.log(`${symbol} 短均线大于长均线，做多`);
            await createBestLimitBuyOrderUntilFilled(symbol, invest);
        }

    } else if (shortCondition) {
        if (position && Number(position.info.positionAmt) < 0) {
            console.log(`${symbol} 已有仓位，不再做空`);
        } else if (position && Number(position.info.positionAmt) > 0) {
            console.log(`${symbol} 已有做多仓位，先平仓后做空`);
            let amount = Math.abs(position.info.positionAmt);
            await createBestLimitSellOrderByAmountUntilFilled(symbol, amount);
            await createBestLimitSellOrderUntilFilled(symbol, invest);
        } else {
            console.log(`${symbol} 短均线小于长均线，做空`);
            await createBestLimitSellOrderUntilFilled(symbol, invest);
        }
    } else {
        console.log('均线相等，不做操作');
    }
}

async function main() {

    // 加载市场
    await exchange.loadMarkets();

    while (true) {
        console.log("策略开始执行: " + new Date());
        try {
            // 趋势策略
            let trendSymbols = emaConfig.trendSymbols;
            for await (let symbol of trendSymbols) {
                try {
                    await ema(symbol, true);
                } catch (e) {
                    console.error(`趋势策略执行异常 ${symbol}`, e);
                }

            }

            // 反转策略
            let reverseSymbols = emaConfig.reverseSymbols;
            for await (let symbol of reverseSymbols) {
                try {
                    await ema(symbol, false);
                } catch (e) {
                    console.error(`反转策略执行异常 ${symbol}`, e);
                }
            }

            // 未选中的币平仓
            let positions = await exchange.fetchPositions();
            positions = positions.filter(x => x.notional !== 0);
            let symbols = trendSymbols.concat(reverseSymbols);
            for (let position of positions) {
                let symbol = position.info.symbol;
                if (!symbols.includes(symbol)) {
                    console.warn(`未选中的币 ${symbol} 平仓`);
                    let amount = Math.abs(position.info.positionAmt);
                    if (Number(position.info.positionAmt) > 0) {
                        await createBestLimitSellOrderByAmountUntilFilled(symbol, amount);
                    } else {
                        await createBestLimitBuyOrderByAmountUntilFilled(symbol, amount);
                    }
                }
            }
        } catch (e) {
            console.error("均线策略异常", e);
            await ding("均线策略异常", e.message);
            break;
        }

        // 每小时执行一次
        await sleep(1000 * 60 * 60 * emaConfig.holdPeriod);

        // 测试使用
        // await sleep(1000);
    }
}

main();
// module.exports = main;

