const { merge } = require('webpack-merge');
const commonConfig = require('./webpack.common.config');

const configuration = [];

commonConfig.forEach((entry) => {
  configuration.push(
    merge(entry, {
      mode: 'production',
      devtool: false,
      ignoreWarnings: [/Failed to parse source map/]
    })
  )
})

module.exports = configuration
