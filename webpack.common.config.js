const path = require('path');
const Dotenv = require('dotenv-webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { createConfig } = require('@edx/frontend-build');

const config = createConfig('webpack-prod');

// Override entries.
config.entry = {
  feedback_carousel: './eox_nelp/course_experience/frontend/src/components/FeedbackCarousel/index',
  tenant_stats: './eox_nelp/stats/frontend/src/components/TenantStats/index',
}

// Override output configuration in order to get a unique folder per entry.
config.output = {
  path: path.resolve('./eox_nelp/static/'),
  filename: '[name]/js/[name].js',
  chunkFilename: '[name]/js/[name].js',
}

// This change is to avoid the default chunks behavior, since this implementation will require a unique file per view.
config.optimization = {
  minimize: true,
}

config.plugins.splice(1, 3,
  new MiniCssExtractPlugin({ // Override MiniCssExtractPlugin in order to change the file name
    filename: '[name]/css/[name].css',
  }),
  new Dotenv({ // Override the Dotenv plugin in order to use env.frontend instead of .env
    path: path.resolve(process.cwd(), '.env.frontend'),
    systemvars: true,
  }),
)

module.exports = config;
