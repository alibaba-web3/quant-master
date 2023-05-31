const path = require('path');

module.exports = {
    target: 'node',
    entry: './index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'index.js',
    },
    node: {
        __dirname: false, //在 Node.js 中，__dirname 是当前模块文件所在的目录的绝对路径。这个选项设置为 false 可以使 __dirname 的行为在打包后的文件中保持与 Node.js 默认的行为一致。
        __filename: false, //这个选项设置为 false 可以使 __filename 的行为在打包后的文件中保持与 Node.js 默认的行为一致。
    },
};
