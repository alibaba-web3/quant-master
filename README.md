# quant-master

量化回测

1. 运行 1_数据准备.py 文件, 下载 spot_1d.csv 文件
2. 运行 2_回测.py 文件

文件目录：
data: 回测所需要的数据
example: 回测案例

pandas 字段约定：
date: 日期
balance: 账户余额
revenueRate: 总收益率
invest: 当天投入
totalInvest 累计投入
currentRevenueRate 本次交易收益率