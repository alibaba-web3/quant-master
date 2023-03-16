const {exchange} = require("./function.js");


async function main() {
    let ticker = await exchange.fetchTicker("BTCUSDT");
    console.log(ticker.close);
}

main();

