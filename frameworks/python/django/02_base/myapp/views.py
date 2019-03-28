# coding: utf8

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'index.html')


def restapi(request, strval, intval):
    return HttpResponse('restapi: strval={} intval={}'.format(strval, intval))


def regexp(request):
    return HttpResponse('regexp')


def get_params(request):
    params = request.GET
    return HttpResponse('get_params: {}'.format(escape(str(params))))


@csrf_exempt
def methods(request):
    # Это ручная форма. Так как правило делать не надо, django умеет сам генерить формы
    # ВАЖНО: все формы в django по умолчанию должны иметь csrf_token.
    # Декоратор csrf_exempt здесь исключает проверку csrf_token-а (иначе будет ошибка)
    # Это сделано только здесь разово, чтобы руками сгенерить простейшую форму
    # В дальнейшем будем пользоваться формами из django

    if request.method == 'POST':
        return HttpResponse('this is a post request')
    else:
        return HttpResponse(
            '''
                This is a get request.
                <form method="POST">
                    <input type=submit value=SEND POST>
                </form>
            '''
        )


def redir_src(request):
    return redirect('redir-dest')


def redir_dest(request):
    return HttpResponse('redirected')


def headers_example(request, header_name):
    key = 'HTTP_{}'.format(header_name).upper()
    return HttpResponse('request header {} = {}'.format(header_name, escape(str(request.META.get(key)))))


@csrf_exempt
def cookie_exapmle(request):
    if request.method == 'POST':
        resp = redirect('cookie')
        resp.set_cookie('djangotest', str(request.POST['setcookie']))
        return resp
    else:
        return HttpResponse(
            '''
                your cookie djangotest = {} <br/>

                <form method="POST">
                    <input type=text name=setcookie>
                    <input type=submit value=SET COOKIE>
                </form>
            '''.format(request.COOKIES.get('djangotest'))
        )


def bad_request(request):
    return HttpResponseBadRequest('BAD! Open console and look 400 code')
