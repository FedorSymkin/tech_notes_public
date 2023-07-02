#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Базовые концепции flask.
# Просто запустите эту программу, она напишет какую страницу надо открыть в браузере.
# Дальше будут ссылки для демонстрации разных концепций.

from flask import (
    Flask,
    url_for,
    render_template,
    request,
    make_response,
    abort,
    redirect,
    session,
    escape,
)


app = Flask(__name__)


# ==================== отдать просто html файл =======================================
@app.route('/')
def root():
    # Демонстрируется концепция шаблонов html. Ну правда, не писать же html внутри питона!
    # Здесь отдаётся просто статический html файл, который содержит ссылки на остальные примеры
    return render_template('index.html')


# ==================== отдать файл с параметрами =======================================
@app.route('/template_params/')
@app.route('/template_params/<name>')
def template_params(name=None):
    # Здесь демонстрируются сразу 2 понятия:
    #   * Динамический шаблон html (см. магию внутри), туда передаётся name как параметр
    #   * Получение параметра name из урла
    return render_template('template.html', name=name)


# ==================== не писать по многу раз пути везде =======================================
@app.route('/urlfor')
def urlfor():
    # Если нужно сделать ссылку на другой путь - не надо тут дублировать путь.
    # Надо сделать эту ссылку через url_for, передав туда название функции, обрабатывающей маршрут.
    # Это позволит не писать по два раза путь.
    return '''
        Links generated with url_for<br/>
        <a href="{url1}">root</a><br/>
        <a href="{url2}">{url2}</a><br/>
    '''.format(
        url1=url_for('root'),
        url2=url_for('template_params'),
    )


# ==================== параметры запроса =======================================
@app.route('/request_params')
def request_params():
    # Доступ к параметрам запроса.
    # Здесь стоит обратить внимание, что этот код небезопасен - можно вставить какую угодно инъекцию
    # через параметры!
    return '''
        <b>Args:</b> {}
        <br/>
        <a href="{}?arg1=val1&arg2=val2&flag">try this</a>
    '''.format(request.args, url_for('request_params'))


# ==================== GET / POST =======================================
@app.route('/methods', methods=['GET', 'POST'])
def methods():
    # Тут всё интуитивно понятно - демонстрируется реакция на разные методы
    # Нужно только заметить, что так в проде делать не стоит - сервер на POST возвращает страницу
    # и при обновлении страницы, браузер будет спрашивать у пользователя, что "отправить ещё раз?"
    # По-правильному надо делать редирект на GET, о редиректах ниже.
    # Ну и дыра в безопасности, аналогично прошлому примеру.

    if request.method == 'POST':
        # Важно: в POST запросе для того, чтобы обратиться к параметрам нужно использовать не args, а form
        return '<b>Your value:</b> {}'.format(request.form.get('name'))
    else:
        return '''
            input something:
            <form method='post' action='/methods'>
                <input type='text' name='name'><br/>
                <button type='submit'>OK</button>
            </form>
        '''


# ==================== redirect =======================================
@app.route('/redirect')
def redirect_concept():
    # Сабж
    return redirect(url_for('redirected'))


@app.route('/redirected')
def redirected():
    # Сюда редиректит пример из '/redirect'.
    # Показывается также доступ к хедерам
    return 'You have been redirected from {}'.format(request.headers.get("Referer"))


# ==================== cookies =======================================
@app.route('/cookies', methods=['GET', 'POST'])
def cookies_concept():
    # Демонстрация работы c cookies.

    if request.method == 'GET':
        # В случае GET получаем куку от клиента средствами flask (или None если нет)
        stored_flasktest = request.cookies.get('flasktest')

        # И показываем её пользователю, предлагая также через формочку её поменять, отправив POST на себя же
        return '''
            We will do experiments with cookie named "flasktest"<br>
            <b>your current flasktest cookie: </b> {flasktest}<br/><br/>

            Input new flasktest cookie:<br/>
            <form method="post">
                <p><input type=text name=flasktest>
                <p><input type=checkbox name="with_redirect">with_redirect
                <p><input type=submit value=OK>
            </form>
        '''.format(flasktest=stored_flasktest)

    else:
        # С случае POST надо поменять куку
        # Получаем новое значение для установки из параметров запроса
        new_flasktest = request.form.get('flasktest')

        # также через параметры приходит флаг, надо ли ставить куки через редирект.
        if 'with_redirect' in request.form:
            # Через редирект более правильно - отдаём редирект на себя же,
            # но на GET, и в том же ответе 3xx ещё и Set-Cookie делаем. Поэтому при обновлении страницы в браузере
            # не будет попытки повторной отправки, и вообще поведение приложения более предсказуемо
            resp = redirect(url_for('cookies_concept'))
            resp.set_cookie('flasktest', new_flasktest)
            return resp
        else:
            # А без редиректа - это для демонстрации того, что set-cookie можно прикрутить в обычному ответу
            # В примерах выще могли вернуть просто строку.
            # Теперь чтобы поставить доп. заголовки надо через make_response
            resp = make_response('<b>updating cookie:</b> {}'.format(new_flasktest))
            resp.set_cookie('flasktest', new_flasktest)
            return resp


# ==================== errors =======================================
@app.route('/errors')
def errors_concept():
    abort(403)


@app.errorhandler(403)
def handler_403(e):
    # чуть выше ответили кодом 403 на пути /error. Здесь демонстрируется, что мы можем
    # поставить свой обработчик на коды ошибок и выдавать своё содержимое страницы
    return 'This is manual 403 handler, error="{}"'.format(e), 403


# ==================== sessions =======================================
# Что такое вообще сессии - см. в другом разделе этого репозитория.

# Работа с сессиями во flask идёт поверх cookies, но с добавлением некоторых мер безопасности.
# Сессия подписывается ключом app.secret_key, чтобы клиент не смог её подделать
# Здесь ключ написан просто рандомно. В реальном случае он должен храниться в секрете.
app.secret_key = b'546lhm89_=ad456dfg4/**-rf'


@app.route('/sessions', methods=['GET', 'POST'])
def sessions():
    """
        В основе работы с сессиями лежит глобальный объект session.
        Чтобы прочитать или установить данные сессии мы просто работаем с этим объектом как с диктом.

        Важный момент в том, что все данные при работе с session хранятся на клиенте в куках.
        session - это просто обёртка над куками, она НЕ реализует хранение сессий в БД на стороне backend.
        В реальной жизни на клиенте нужно хранить не все данные сессии, а минимально возможные (например
        userid / sessionid или даже просто sessionid), чтобы сессию можно было быстро инвалидировать при угрозах
        безопасности.
    """

    if request.method == 'GET':
        # GET запрос. Браузер пользователя может отправить куку с сессией.
        # Если есть сессия, покажем это пользователю и предложим выйти.
        # Если нет сессии, поприветствуем гостя и предложим залогиниться.
        if 'username' in session:
            return '''
                Logged in as {name}<br/>
                <br/>
                <form method="post">
                    <input type="hidden" name="action" value="logout">
                    <p><input type=submit value=logout>
                </form>

            '''.format(name=session['username'])
        else:
            return '''
                Welcome, guest. Please, log in.<br/>

                <form method="post">
                    <input type="hidden" name="action" value="login">
                    <p><input type=text name=username>
                    <p><input type=submit value=login>
                </form>
            '''.format()

    else:
        # POST запрос - либо создаём сессию, либо наоборот завершаем.
        # И редиркетим пользователя на GET,
        action = request.form.get('action')
        if action == 'login':
            session['username'] = request.form['username']
            return redirect(url_for('sessions'))

        elif action == 'logout':
            session.pop('username', None)
            return redirect(url_for('sessions'))

        else:
            abort(400)


# ==================== file uploads =======================================
# upload файлов идёт через request.files. Оттуда получаем объекты которые в целом
# ведут себя как питонячие файлы

@app.route('/file_uploads', methods=['GET', 'POST'])
def file_uploads():
    if request.method == 'GET':
        return '''
            <h1>Upload new File</h1>

            <form method=post enctype=multipart/form-data>
                <p><input type=file name=file1>
                <input type=submit value=Upload>
            </form>
        '''

    elif request.method == 'POST':
        f = request.files['file1']
        return 'file content: {}'.format(str(f.read()))

        # Сохранить можно так:
        # f.save('/var/www/uploads/uploaded_file.txt')

    else:
        abort(400)


# ==================== escape =======================================

@app.route('/escape', methods=['GET', 'POST'])
def escape_concept():
    # Должен быть не заголовок, а текст как есть, потому что экранируются символы, чувсвтительные для html.
    # Полезно использовать эту штуку для защиты от всяческих html инъекций.
    return escape('<h1>Escaped text</h1>')


if __name__ == "__main__":
    app.run(debug=True)
