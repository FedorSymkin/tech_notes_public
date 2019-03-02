//Пример конфига webpack, чуть более близкого к реальной ситуации.
//Код взят из https://github.com/iliakan/webpack-screencast/blob/master/01-intro/webpack.config.js
//Добавлены комментарии по видео к этому коду: https://learn.javascript.ru/screencast/webpack#webpack-2-simple-1
//Это выполняется на машине разработчика в node.js

'use strict';

//переменная внутри этого js, которая может быть получена из переменной среды
const NODE_ENV = process.env.NODE_ENV || 'development';

//конфиг вебпака импортирует модуль вебпака для того, чтобы использовать его для некоторых возможностей
const webpack = require('webpack');

module.exports = {
  //исходный файл
  entry:  "./home",
  
  output: {
    //имя файла на выход  
    filename: "build.js",
    
    //название нашей библиотеки, чтобы из неё потом можно было импортировать функции в сторонних скриптах
    library:  "home"
  },

  //режим watch - webpack не завершается, а следит за изменениями исходных файлов и пересобирает при изменениях,
  //причем делает это только если сборка в окружении development
  watch: NODE_ENV == 'development',

  watchOptions: {
    //небольшой тюнинг режима watch - проверяем изменения каждые 100 мс
    aggregateTimeout: 100
  },

  //в режиме development применяем cheap-inline-module-source-map, подробнее в readme
  devtool: NODE_ENV == 'development' ? "cheap-inline-module-source-map" : null,

  plugins: [
    //подключаем плагин DefinePlugin - это про то, что прокинуть 
    //в код js на клиенте значение переменной среды при сборке
    //Т.е. как видно здесь мы можем влиять на поведение js 
    //на клиенте в зависимости от типа сборки
    new webpack.DefinePlugin({
      NODE_ENV: JSON.stringify(NODE_ENV),
      LANG:     JSON.stringify('ru')
    })
  ],

  //это про то где искать исходные файлы 
  //(т.е. модули в терминах вебпака)
  // ./home, который мы подгружаем наверху как исходный файл,
  // тоже считается модулем
  resolve: {
    //это стандартная директория, если не указана директория
    modulesDirectories: ['node_modules'],
    
    //это расширения которые пробуем искать
    extensions:         ['', '.js']
  },

  //это аналонгично но для лоадеров. Что такое лоадеры см. ниже по коду
  resolveLoader: {
    modulesDirectories: ['node_modules'],
    
    //это если в качестве лоадера передан babel, то соответствующий ему модуль 
    //надо искать как babel-loade (в первом случае) или просто как babel (во втором случе)
    moduleTemplates:    ['*-loader', '*'],
    
    //какие бывают расширения для лоадеров
    extensions:         ['', '.js']
  },


  module: {
    loaders: [{
      //при сборке для всех файлов которые заканчиываются на .js (регулярка). 
      //test - это зарезервированное поле для такого объявления, 
      //типа "если test файла на регулярку, тогда применить"
      test:   /\.js$/,
      
      //применяем к такому js файлу преобразователь (loader) babel с параметром optional[]=runtime
      loader: 'babel?optional[]=runtime'
    }]

  }

};


if (NODE_ENV == 'production') {
  //для продакшена подключаем UglifyJsPlugin,
  //которые превращает наш js в однострочник, 
  //вырезает всякие if (false) {...} и т.д.
    
  module.exports.plugins.push(
      new webpack.optimize.UglifyJsPlugin({
        compress: {
          // don't show unreachable variables etc
          warnings:     false,
          drop_console: true,
          unsafe:       true
        }
      })
  );
}