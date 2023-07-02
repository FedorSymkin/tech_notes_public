#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import time
from utils import test_cursor, setup_logging, do_test



def worker_using_sql(nworker):
    """
    Демонстрируется атомарный запрос,
    где увеличиваем переменную только средствами SQL,
    защита от гонок не требуется
    """
    log = logging.getLogger('worker_using_sql-{}'.format(nworker))
    try:
        with test_cursor() as cursor:
            log.info('+10')
            cursor.execute('UPDATE wallets SET money = money + 10 WHERE id = 1')

    except (Exception, OSError):
        log.exception('fatal')


def worker_without_locks(nworker):
    """
    Пример когда изменения делаются в две стадии - чтение + запись.
    Выполнение этого из параллельных процессов приводит к нарушению консистентности
    После выполнения этих воркеров сумма будет не 200, а между 100 и 200
    """
    log = logging.getLogger('worker_without_locks-{}'.format(nworker))
    try:
        with test_cursor() as cursor:
            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old = int(cursor.fetchone()[0])
            money_new = money_old + 10
            log.info('{} -> {}'.format(money_old, money_new))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new))

    except (Exception, OSError):
        log.exception('fatal')


def worker_with_sync_lock(nworker):
    """
    Пример изменений в две стадии, которые защищены синхронным локом на row таблицы
    """
    log = logging.getLogger('worker_with_sync_lock-{}'.format(nworker))

    try:
        with test_cursor() as cursor:
            # Получаем лок синхронно - залипаем здесь если лок занят
            log.info('trying to get lock')
            cursor.execute('SELECT pg_advisory_lock(id) FROM wallets WHERE id = 1;')

            # Меняем данные вручную, это выполняется под локом
            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old = int(cursor.fetchone()[0])
            money_new = money_old + 10
            log.info('{} -> {}'.format(money_old, money_new))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new))

    except (Exception, OSError):
        log.exception('fatal')


def worker_with_async_lock(nworker):
    """
    Пример изменений в две стадии, которые защищены асинхронным локом на row таблицы -
    при неудачной попытке взять лок, не залипаем, а получаем False результат
    """
    log = logging.getLogger('worker_with_async_lock-{}'.format(nworker))

    try:
        with test_cursor() as cursor:

            # Пробуем получить лок асинхронно, если не получилось - ждём и пробуем ещё раз
            log.info('trying to get lock')
            while True:
                cursor.execute('SELECT pg_try_advisory_lock(id) FROM wallets WHERE id = 1;')
                res = cursor.fetchone()[0]
                if res:
                    break
                log.info('wait')
                time.sleep(0.1)

            # Меняем данные вручную, это выполняется под локом
            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old = int(cursor.fetchone()[0])
            money_new = money_old + 10
            log.info('{} -> {}'.format(money_old, money_new))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new))

    except (Exception, OSError):
        log.exception('fatal')


def worker_session_level(nworker):
    """
    Демонстрация неправильной ситуации, когда лок держится на протяжении всей сессии
    (т.е. до разрыва соединения), что замедляет остальные воркеры
    """
    log = logging.getLogger('worker_session_level-{}'.format(nworker))

    try:
        with test_cursor() as cursor:
            # Получаем лок синхронно - залипаем здесь если лок занят
            log.info('trying to get lock')
            cursor.execute('SELECT pg_advisory_lock(id) FROM wallets WHERE id = 1;')

            # Меняем данные вручную, это выполняется под локом
            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old = int(cursor.fetchone()[0])
            money_new = money_old + 10
            log.info('{} -> {}'.format(money_old, money_new))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new))

            # Допустим воркер ещё некоторое время что-то делает.
            # В это время лок занят - другие воркеры ждут
            time.sleep(1)

    except (Exception, OSError):
        log.exception('fatal')


def worker_transaction_level(nworker):
    """
    Демонстрация лока на уровне транзакции - лок освобождается с завершением транзакции
    """
    log = logging.getLogger('worker_with_sync_lock-{}'.format(nworker))

    try:
        with test_cursor() as cursor:
            # Получаем лок синхронно - залипаем здесь если лок занят
            log.info('trying to get lock')
            cursor.execute('BEGIN;')
            cursor.execute('SELECT pg_advisory_xact_lock(id) FROM wallets WHERE id = 1;')

            # Меняем данные вручную, это выполняется под локом
            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old = int(cursor.fetchone()[0])
            money_new = money_old + 10
            log.info('{} -> {}'.format(money_old, money_new))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new))

            cursor.execute('COMMIT;')

            # допустим воркер ещё некоторое время что-то делает
            # Транзакция завершена, поэтому другие воркеры здесь не ждут
            time.sleep(1)

    except (Exception, OSError):
        log.exception('fatal')


def worker_several_rows(nworker):
    """
    Пример того, как берём лок сразу на несколько строк
    """
    log = logging.getLogger('worker_several_rows-{}'.format(nworker))

    # пусть каждый 2-й воркер будет лочить и менять сразу 2 записи
    both = bool(nworker % 2)

    try:
        with test_cursor() as cursor:
            log.info('trying to get lock')

            # Демонстрируем как можно взять в одном месте лок на обе строки, а в другом - лок на одну из этих строк
            if both:
                cursor.execute('SELECT pg_advisory_lock(id) FROM wallets WHERE id in (1, 2);')
            else:
                cursor.execute('SELECT pg_advisory_lock(id) FROM wallets WHERE id = 1;')

            cursor.execute('SELECT money FROM wallets WHERE id = 1')
            money_old1 = int(cursor.fetchone()[0])

            cursor.execute('SELECT money FROM wallets WHERE id = 2')
            money_old2 = int(cursor.fetchone()[0])

            money_new1 = money_old1 + 10
            money_new2 = money_old2 + 10

            log.info('{} -> {} for 1'.format(money_old1, money_new1))
            cursor.execute('UPDATE wallets SET money={} WHERE id=1'.format(money_new1))

            if both:
                log.info('{} -> {} for 1'.format(money_old1, money_new2))
                cursor.execute('UPDATE wallets SET money={} WHERE id=2'.format(money_new2))

    except (Exception, OSError):
        log.exception('fatal')


def main():
    setup_logging()
    do_test(worker_using_sql, 'USING_SQL')
    do_test(worker_without_locks, 'WITHOUT_LOCKS')
    do_test(worker_with_sync_lock, 'SYNC LOCKS')
    do_test(worker_with_async_lock, 'ASYNC LOCKS')
    do_test(worker_session_level, 'SESSION LEVEL')
    do_test(worker_transaction_level, 'TRANSACTION LEVEL')
    do_test(worker_several_rows, 'SEVERAL ROWS')


if __name__ == '__main__':
    main()
