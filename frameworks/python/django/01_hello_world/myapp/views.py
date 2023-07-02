# coding: utf8

"""
Здесь живут обработчики запросов, которые привязаны к путям в urls.py.
В терминах django (и парадигмы MVC) такой обработчик называется View, поэтому файл views.py
"""


from django.http import HttpResponse


def home(request):
    return HttpResponse('hello world from django!')


def stuff(request):
    return HttpResponse('stuff from django!')
