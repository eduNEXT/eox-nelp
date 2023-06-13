const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {

    context: __dirname,

    entry: {
        feedback_carousel: './eox_nelp/course_experience/src/components/FeedbackCarousel/index',
        // tenant_stats: './eox_nelp/course_experience/src/components/TenantStats/index'
    },
    output: {
        path: path.resolve('./eox_nelp/course_experience/static/js/'),
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            }
        ]
    },
    resolve: {
        extensions: ['*', '.js', '.jsx']
    },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          format: {
            comments: false,
          },
        },
        extractComments: false,
      }),
    ],
  },
};
