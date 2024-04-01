const { merge } = require('webpack-merge');
const commonConfig = require('./webpack.common.config');

const configuration = [];

commonConfig.forEach((entry) => {
  configuration.push(
    merge(entry, {
      mode: 'development',
      devtool: 'eval-source-map',
    })
  )
})

module.exports = configuration
