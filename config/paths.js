const path = require('path')

module.exports = {
  root: path.resolve(__dirname, '../'),

  // Source files
  src: path.resolve(__dirname, '../src'),

  // Assets
  assets: path.resolve(__dirname, '../assets'),

  // Production build files
  build: path.resolve(__dirname, '../staticfiles'),

  // Static files that get copied to build folder
  public: path.resolve(__dirname, '../public'),
}
