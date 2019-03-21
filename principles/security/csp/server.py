#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Демонстрация принципов CSP.
Сервер, который запускается либо как основной либо как "злой"
"""

import argparse
import logging
from flask import Flask, send_from_directory, request, render_template
from flask_socketio import SocketIO, emit

# args
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--evil', help='attacker server mode', action='store_true')
parser.add_argument('-c', '--csp', help='use CSP', action='store_true')
args = parser.parse_args()
evil = args.evil
use_csp = args.csp
server_name = 'EVIL' if evil else 'MAIN'
port = 9051 if evil else 9050

# logging
logging.basicConfig(level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"))
logging.getLogger().handlers = [console_handler]
log = logging.getLogger('server {}'.format(server_name))


# flask & socketIO
app = Flask(__name__, static_folder='public', template_folder='public')
app.config['SECRET_KEY'] = 'fgdfys5rto34854umrhfks'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', name=server_name)


@app.route('/some_dynamic_resource/<data>', methods=['GET', 'POST'])
def some_dynamic_resource(data):
    log.info('>>>>>>>>>>>>>>>>>>> Got data from client by ajax: {}, method: {}'.format(data, request.method))
    return 'ajax hello from {}, data={}'.format(server_name, data)


@app.route('/<path>')
def something(path):
    return send_from_directory(app.static_folder, path)


@socketio.on('msg', namespace='/wstest')
def message(data):
    log.info('>>>>>>>>>>>>>>>>>>> got data from websocket data={}'.format(data))
    emit('reply', 'data echo via websocket: {}'.format(data))


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache"

    # Вот здесь в хедерах мы включаем CSP
    if use_csp:
        csp_rules = [
            "default-src 'self'",

            # Раскомментируйте, если хотите попробовать разрешить всякие inline на странице
            # "script-src 'unsafe-eval' 'unsafe-inline'",
        ]
        r.headers["Content-Security-Policy"] = ' '.join(csp_rules)

    return r


socketio.run(app, debug=True, port=port)
