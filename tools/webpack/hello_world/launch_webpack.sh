#!/bin/bash

# Запускаем исходя из того, что webpack был установлен локально, без sudo.
# Есть возможно также поставить webpack глобально: 
# sudo npm i webpack 
# и тогда можно запускать проще: webpack

node node_modules/webpack/bin/webpack.js

