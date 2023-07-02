# Сетевое программирование на C/C++

## Meta
* В стандартной библиотеке C++ нет сокетов из коробки
* Поэтому пути работы с сокетами такие:
    * Руками через системные вызовы socket, connect, bind, accept и т.д. (речь про POSIX), да здравствует чистый C
    * Популярные библиотеки, например boost.asio
    * Велосипеды! Как минимум инкапсулировать всю эту сишную жуть в свои классы.
* Главное - TCP / UDP. Всё остальное (Raw sockets, ICMP) - пока за скобками
* TCP гарантирует доставку и требует предварительную установку соединения
* UDP - **не** гарантирует, и **не** требует предварительную установку соединения

## Примеры
* TCP/UDP client/server на системных вызовах - [src/client_server/README.md](src/client_server/README.md)
* select - [src/example_select/README.md](src/example_select/README.md)
* boost.asio - [src/boost_asio/README.md](src/boost_asio/README.md)