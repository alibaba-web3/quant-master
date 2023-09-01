const fs = require("fs");
const path = require('path');
const {exchange, getBestPrice, sleep, readConfig, updateAllLeverage} = require("./function.js");
const process = require("process");

const config = readConfig();

async function main() {
    console.log("程序开始执行");
    // let ticker = await exchange.fetchTicker("BTCUSDT");
    // console.log("当前BTC价格:", ticker.close);

    console.log("当前运行环境: ", config.env);

    await updateAllLeverage(10);
}

main();

