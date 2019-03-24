# Самый первый hello world на django

## Как запускать

```
sudo pip3 install django
```

```bash
$ python3 -m django --version
2.*.*
```

```bash
Эти действия делать не нужно, здесь просто показано как был создан проект

$ django-admin startproject hello_world
$ cd hello_world
$ python3 manage.py startapp myapp

Эти команды генерят базовый каркас для проекта
```

```
hello_world$ python3 manage.py runserver
```

http://127.0.0.1:8000/myapp
http://127.0.0.1:8000/myapp/stuff

## Как всё устроено
* `django-admin startproject` генерит базовый проект, несколько файлов, смысл которых описан в коде
* `manage.py` - это точка входа для разработческих действий над проектом
* `python3 manage.py startapp` генерит код для под-приложения в составе проекта. Именно в под-приложении пишется основной код
* Смысл файлов под-приложения также описан в коде
* `python3 manage.py runserver` запускает http-сервер. Точки входа см в файле `hello_world/urls.py`
* Пока что это элементарный hello world, который по двум путям выводит разные надписи