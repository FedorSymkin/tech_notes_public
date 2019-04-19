# -*- coding: utf-8 -*-

import logging
import psycopg2
import multiprocessing as mp
from contextlib import contextmanager


def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s]: %(message)s"))
    logging.getLogger().handlers = [console_handler]


@contextmanager
def test_cursor():
    conn = psycopg2.connect(
        host='localhost',
        user='djtest',
        password='djtestpass',
        dbname='test',
    )
    cursor = conn.cursor()
    yield cursor
    conn.commit()
    cursor.close()
    conn.close()


def mkdata():
    with test_cursor() as cursor:
        cursor.execute(
            '''
            DROP TABLE IF EXISTS "wallets";

            CREATE TABLE "wallets" (
                "id" SERIAL NOT NULL PRIMARY KEY,
                "user" int NOT NULL,
                "money" int NOT NULL
            );

            INSERT INTO wallets("user", "money") VALUES (1, 100);
            INSERT INTO wallets("user", "money") VALUES (2, 100);
            INSERT INTO wallets("user", "money") VALUES (3, 100);
            '''
        )


def do_multiprocessing(entry_point, process_count):
    pool = mp.Pool(process_count)
    pool.map_async(entry_point, [i for i in range(process_count)])
    pool.close()
    pool.join()


def print_data(mark):
    print(mark + ':')
    with test_cursor() as cursor:
        cursor.execute('select * from wallets order by id')
        for row in cursor.fetchall():
            print(row)


def do_test(worker_func, mark, process_count=10):
    print('============== {} ================'.format(mark))
    mkdata()
    print_data('INITIAL DATA')
    do_multiprocessing(worker_func, process_count=process_count)
    print_data('Result')
    print('\n\n\n')
