/*
Файл взят из https://github.com/learncodeacademy/react-js-tutorials/blob/master/1-basic-react
Добавлены комментарии.
Видео: https://www.youtube.com/watch?v=MhkGQAoc7bc&list=PLoYCgNOIyGABj2GQSlDRjgvXtqfDxKm5b
*/

var debug = process.env.NODE_ENV !== "production";
var webpack = require('webpack');
var path = require('path');

module.exports = {

  //откуда брать исходники
  context: path.join(__dirname, "src"),

  //про source-map подробнее рассказано в разделе про webpack
  devtool: debug ? "inline-sourcemap" : false,

  //точка входа js - там будем писать код, оттуда будем импортировать реакт
  entry: "./entry.js",

  module: {
    rules: [
      {
        //Все файлы js c помощью babel-я превращаем в нативный js
        test: /\.js?$/,

        //исключая содержимое node_modules и bower_componentsы
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',

        //это настройки в бабель
        query: {
          presets: ['react', 'es2015', 'stage-0'],
          plugins: ['react-html-attrs', 'transform-decorators-legacy', 'transform-class-properties'],
        }
      }
    ]
  },
  output: {
    path: __dirname + "/src/",
    filename: "build.js"
  },
  plugins: debug ? [] : [
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurrenceOrderPlugin(),
    new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
  ],

  // Это важная настройка для того чтобы webpack-dev-server выдавал всегда одну страницу независимо от пути. Зачем - см. код
  devServer: {
      historyApiFallback: true
  }
};
