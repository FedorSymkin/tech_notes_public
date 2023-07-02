#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask

# создаём приложение из текущего файла
app = Flask(__name__)


# всё максимально просто - функции декорируются путями из url-ов.
# Т.е. по запросу http://localhost:5000/ вызовется эта функция
@app.route("/")
def root():
    return '''
        <h1>Flask hello world</h1>
        <a href="/some_route">click me</a>
    '''


# А это вызовется по запросу http://localhost:5000/some_route
@app.route("/some_route")
def some_route():
    return 'some info blah-blah-blah'


# Вот насолько до безумия просто запускается http сервер из фласка. По умолчанию будет работать на порту 5000.
# В любом случае в stdout напишет куда ходить.
if __name__ == "__main__":
    app.run()

# есть ещё другой способ запустить сервер на flask-е, без main:
# export FLASK_APP=hello_world.py ; flask run
