const { merge } = require('webpack-merge');
const commonConfig = require('./webpack.common.config');

module.exports = merge(commonConfig, {
  mode: 'production',
  devtool: false,
  ignoreWarnings: [/Failed to parse source map/]
})
