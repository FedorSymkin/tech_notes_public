# Tiny C++ http client, STL only

```bash
$ ./cpp_http_client 127.0.0.1:8000 > output.html
GET '127.0.0.1:8000'
response OK:
STATUS 200
HEADERS:
Allow: GET, HEAD, OPTIONS
Content-Length: 67632
Content-Type: text/html; charset=utf-8
Date: Tue, 14 May 2019 00:14:47 GMT
Server: WSGIServer/0.2 CPython/3.7.3
Vary: Accept, Cookie
X-Frame-Options: SAMEORIGIN
CONTENT FACT SIZE: 67632
=================
```

* Follows 3xx Redirects
* Any content (html, pictures, binary data, etc...)
* https is not supported
* 1xx responses are not supported
