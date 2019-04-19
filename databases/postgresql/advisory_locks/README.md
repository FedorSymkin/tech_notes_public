# Advisory locks в postgresql

* Локи строк таблиц, используемые в приложении (как мьютексы)
* На логику работы самого postgres не влияет
* Есть автоматическое отпускание лока при завершении связи с БД
* Есть автоматическое отпускание лока при завершении транзакции
* Есть ручное отпускание лока
* Можно залочить как отдельную строку, так и несколько строк
* Есть exclusive и shared

## Источники
* https://www.postgresql.org/docs/9.4/explicit-locking.html
* https://vladmihalcea.com/how-do-postgresql-advisory-locks-work/

## Что показано в примере 
* Есть таблица из 3 строк
* В одной из строк стоит значение money=100
* Его увеличивают 10 параллельных процессов, каждый на 10 единиц
* При правильной работе ожидаем получить значение 200, например:
```
============== SYNC LOCKS ================
INITIAL DATA:
(1, 1, 100)
(2, 2, 100)
(3, 3, 100)
2019-04-19 18:48:14,404 [worker_with_sync_lock-4]: trying to get lock
2019-04-19 18:48:14,404 [worker_with_sync_lock-5]: trying to get lock
2019-04-19 18:48:14,405 [worker_with_sync_lock-3]: trying to get lock
2019-04-19 18:48:14,405 [worker_with_sync_lock-7]: trying to get lock
2019-04-19 18:48:14,405 [worker_with_sync_lock-2]: trying to get lock
2019-04-19 18:48:14,407 [worker_with_sync_lock-4]: 100 -> 110
2019-04-19 18:48:14,407 [worker_with_sync_lock-0]: trying to get lock
2019-04-19 18:48:14,410 [worker_with_sync_lock-9]: trying to get lock
2019-04-19 18:48:14,412 [worker_with_sync_lock-5]: 110 -> 120
2019-04-19 18:48:14,413 [worker_with_sync_lock-1]: trying to get lock
2019-04-19 18:48:14,416 [worker_with_sync_lock-6]: trying to get lock
2019-04-19 18:48:14,418 [worker_with_sync_lock-3]: 120 -> 130
2019-04-19 18:48:14,420 [worker_with_sync_lock-8]: trying to get lock
2019-04-19 18:48:14,423 [worker_with_sync_lock-7]: 130 -> 140
2019-04-19 18:48:14,431 [worker_with_sync_lock-0]: 140 -> 150
2019-04-19 18:48:14,436 [worker_with_sync_lock-2]: 150 -> 160
2019-04-19 18:48:14,441 [worker_with_sync_lock-9]: 160 -> 170
2019-04-19 18:48:14,447 [worker_with_sync_lock-1]: 170 -> 180
2019-04-19 18:48:14,452 [worker_with_sync_lock-6]: 180 -> 190
2019-04-19 18:48:14,456 [worker_with_sync_lock-8]: 190 -> 200
Result:
(1, 1, 200)
(2, 2, 100)
(3, 3, 100)
```
* Показаны разные примеры, в т.ч. неправильный, как нарушается консистентность при гонках без локов