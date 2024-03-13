const path = require('path');
const Dotenv = require('dotenv-webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { createConfig } = require('@edx/frontend-build');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const configuration = [];

// Set entries.
const entries = {
  feedback_carousel: './eox_nelp/course_experience/frontend/src/components/FeedbackCarousel/index',
  tenant_stats: './eox_nelp/stats/frontend/src/components/TenantStats/index',
}

Object.entries(entries).forEach((entry) => {
  const [key, value] = entry;
  const config = createConfig('webpack-prod');

  // Override entries.
  config.entry = {
    [key]: value,
  }

  // Override output configuration in order to get a unique folder per entry.
  config.output = {
    path: path.resolve(`./eox_nelp/static/${key}`),
    filename: 'js/[name].js',
    chunkFilename: 'js/[name].js',
  }

  // This change is to avoid the default chunks behavior, since this implementation will require a unique file per view.
  config.optimization = {
    minimize: true,
  }

  // Override frontend-platform  default plugins
  const existingPluginsCopy = config.plugins.slice();

  existingPluginsCopy.splice(2, 1, new CleanWebpackPlugin())
  existingPluginsCopy.splice(3, 3,
    new MiniCssExtractPlugin({ // Override MiniCssExtractPlugin in order to change the file name
      filename: 'css/[name].css',
    }),
    new Dotenv({ // Override the Dotenv plugin in order to use env.frontend instead of .env
      path: path.resolve(process.cwd(), '.env.frontend'),
      systemvars: true,
    }),
  )
  config.plugins = [... existingPluginsCopy]

  configuration.push(config);
})

module.exports = configuration;
