const path = require('path');
const Dotenv = require('dotenv-webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { createConfig } = require('@openedx/frontend-build');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const configuration = [];

// Set entries.
const entries = {
  tenant_stats: {
    js: './eox_nelp/stats/frontend/src/components/TenantStats/index',
    template: 'eox_nelp/stats/templates/tenant_stats.html',
  },
  feedback_carousel: {
    js: './eox_nelp/course_experience/frontend/src/components/FeedbackCarousel/index',
    template: 'eox_nelp/course_experience/frontend/templates/feedback_courses.html',
  },
  user_profile: {
    js: './eox_nelp/user_profile/frontend/src/components/UserProfileForm/index',
    template: 'eox_nelp/user_profile/templates/user_profile_form.html',
  },
}

Object.entries(entries).forEach((entry) => {
  const [key, value] = entry;
  const config = createConfig('webpack-prod');

  // Override entries.
  config.entry = {
    [key]: value['js'],
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

  existingPluginsCopy.splice(2, 1, new CleanWebpackPlugin({
    cleanOnceBeforeBuildPatterns: [
        '!__init_.py',
    ]
  }))
  existingPluginsCopy.splice(3, 3,
    new MiniCssExtractPlugin({ // Override MiniCssExtractPlugin in order to change the file name
      filename: 'css/[name].css',
    }),
    new HtmlWebpackPlugin({
      inject: true,
      minify: false,
      publicPath: `/static/${key}/`,
      template: path.resolve(process.cwd(), value['template']),
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
