# django rest api framework authentication

В примере показаны одновременно 2 типа аутентификации пользователей при работе с REST API:

* По токену (например для роботов)
* По сессии (например из браузера / AJAX) 

## Источники
* https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
* https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication

## Регистрация и аутентификация в API по токену
* Вообще без браузера, всё только по API, в примере см директорию scripts - там всё делается через curl
* Модель пользователя та же, что и в обычном django - django.contrib.auth.models.User
* Для регистрации пользователя через API есть отдельный path (в примере это `/api/register`). Под ним делается свой View и Serializer вокруг встроенной модели пользователя. Туда сходить с POST запросом и сообщить информацию о новом пользователе - как минимум логин и пароль.
* После регистрации пользователю нужно получить API токен. Для этого есть ещё один path (в примере - `/api/get_token`). На него нужно сделать отдельный **POST запрос (не GET)**, передав логин и пароль в json. Под этим path - стандартный view, встроенный в rest api framework. Почему POST? Потому что изначально токена нет. Он создаётся в базе при запросе.
* Далее в запросах токен передаётся через http заголовок
* Получение токена от пользователя в запросах и превращение его в user - из коробки поддержано в rest api framework (сам собой появляется объект request.user так же как и для сессий)
* У каждого view в rest api framework можно прописать требуется ли аутентификация пользователя, а также дополнительные условия, например что сообщение может редактировать только его автор.
* Также стандартные настройки доступа для views можно выставлять по умолчанию в settings.py
* Протухания токена из коробки нет: https://stackoverflow.com/questions/22943050/how-long-is-token-valid-django-rest-framework
* В файле `token_storage_details.txt` немного подробностей о том как хранятся токены в базе

## Как запускать скрипты чтобы попробовать примеры API по токену
```
Подготовка
sudo apt-get install curl jq
.../10_rest_users$ python3 manage.py runserver

Создаём пользователей (ходит на /api/register)
.../10_rest_users/scripts$ ./create_user.sh user1 user1pass
.../10_rest_users/scripts$ ./create_user.sh user2 user2pass

Создаём сообщения (ходит на /api/posts/new)
.../10_rest_users/scripts$ ./create_message.sh user1 user1pass hello1 world1
.../10_rest_users/scripts$ ./create_message.sh user2 user2pass hello2 world2

Просмотрим сообщения (ходит на /api/posts, пример сделан так, что смотреть сообщения могут только залогиненные пользователи)
./get_all_posts.sh user1 user1pass

И т.д, ещё есть edit_title.sh для демонстрации того, что пользователи могут редактировать только свои сообщения
```


## Аутентификация по сессиям
* Регистрация пользовалеля из браузера в примере не показана - уже было про это в прошлых разделах. Но ничто не мешает сделать
* login/logout через html формы а браузере
* Далее в запросы пробрасываются куки/сессии (в т.ч. должны и через AJAX пробрасываться), и оттуда образуется тот же объект request.user.
* Что будет если в заголовках перехать и куки с сессиями и токен, но от другого пользователя - не проверял.

## В целом
* Для кода, который обращается в request.user, вообще без разницы как идёт аутентификация - по токену или по сессии
* Не забыть включить в INSTALLED_APPS:
```
'rest_framework',
'rest_framework.authtoken',
```

* Также в settings.py явно прописано
```
REST_FRAMEWORK = {
     'DEFAULT_AUTHENTICATION_CLASSES': (
         'rest_framework.authentication.TokenAuthentication',
         'rest_framework.authentication.SessionAuthentication',
     )
}
```
По желанию можно выбирать доступные механизмы аутентификации.