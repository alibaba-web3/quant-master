const {exchange} = require("./function.js");
const axios = require('axios');
const {createBestLimitBuyOrder} = require("./function");

async function getDefiLlamaTVL(protocol) {
    try {
        const response = await axios.get(`https://api.llama.fi/protocol/${protocol}`);
        return response.data.tvl.map((item) => {
            return {...item, date: new Date(item.date * 1000)};
        });
    } catch (error) {
        console.error(error);
    }
}


async function main() {
    // 查询 makerdao 的 TVL 数据
    let tvlList = await getDefiLlamaTVL('makerdao');
    if (tvlList && tvlList.length > 1) {
        let last = tvlList[tvlList.length - 1];
        let last2 = tvlList[tvlList.length - 2];
        let last3 = tvlList[tvlList.length - 3];

        // TVL 最后一条数据是当前时间，其余数据是UTC时间 0 点
        if (last.date.getDate() === last2.date.getDate() && last2.totalLiquidityUSD > last3.totalLiquidityUSD) {
            // TVL 上涨时买入
            // await createBestLimitBuyOrder("BTCUSDT", 100);
        } else if (last.date.getDate() === last2.date.getDate() && last2.totalLiquidityUSD <= last3.totalLiquidityUSD) {
            // TVL 下跌时卖出
            // await createBestLimitSellOrder("BTCUSDT", 100);
        }

    }

}

main();

