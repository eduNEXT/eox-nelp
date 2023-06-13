const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const Dotenv = require('dotenv-webpack');


module.exports = {

    context: __dirname,

    entry: {
        feedback_carousel: './eox_nelp/course_experience/frontend/src/components/FeedbackCarousel/index',
        // tenant_stats: './eox_nelp/course_experience/src/components/TenantStats/index'
    },
    output: {
        path: path.resolve('./eox_nelp/static/js/'),
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            },
            {
              test: /\.(ts|tsx)$/,
              exclude: /node_modules/,
              use: [
                {
                  loader: 'babel-loader',
                  options: {
                    presets: ['@babel/preset-react', '@babel/preset-typescript'],
                  },
                },
                {
                  loader: 'ts-loader',
                },
              ],
            },
            {
              test: /\.scss$/,
              use: ['style-loader', 'css-loader', 'sass-loader'],
            },
            {
              test: /\.svg$/,
              use: ['svg-url-loader'],
            },
        ]
    },
    resolve: {
        extensions: ['.ts', '.tsx', '.js', '.jsx'],
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
  plugins: [
    new Dotenv({
        path: path.resolve(process.cwd(), '.env.frontend'),
        systemvars: true,
    }),
  ]
};
