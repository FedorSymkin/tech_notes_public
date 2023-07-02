#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Чтобы понять этот пример, очень желательно понять сначала пример из meta.py

Как было показано в base.py из корутин можно отдавать управление через await asyncio.something.
Но что если нам надо сделать что-то, чего нет в asyncio?
Т.е. сказать await some_generic_io() ? Упадёт, потому что конструкция await предполагает что будет
отдан некоторый awaitable объект.

Следовательно, если надо из корутины отдать ожидание какого-то общего кода, не из asyncio,
надо этот код завернуть в awaitable объект либо использовать asyncio.Future

Ниже показаны примеры как это сделать
test_bad - формулировка проблемы
test_other_thread_with_future - демонстрация ожидания какого-то события вручную через asyncio.Future
test_other_thread_with_awaitable - демонстрация ожидания какого-то события вручную через свой awaitable объект
"""

import time
import asyncio
import threading


def test_bad():
    print("============= TEST BAD ==================")

    def some_generic_io():
        # допустим это какой-то блокирующий запрос, которые не может быть реализован через asyncio
        # Более того, мы не можем pull-ить события, а можем только заснуть
        time.sleep(1)

    async def foo():
        try:
            print('start foo')
            await some_generic_io()  # TypeError: object NoneType can't be used in 'await' expression
            print('end foo')
        except Exception as e:
            print('exception: {}'.format(e))

    ioloop = asyncio.new_event_loop()
    tasks = [ioloop.create_task(foo())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


def test_other_thread_with_future():
    print("============= TEST OTHER THREAD WITH FUTURE ==================")

    ioloop = asyncio.new_event_loop()

    def some_generic_io(future):
        # Допустим это какой-то блокирующий запрос, которые не может быть реализован через asyncio
        # Более того, мы не можем pull-ить события, а можем только заснуть
        time.sleep(1)

        # Важно понимать, что это другой поток.
        # дёргаем asyncio-шную фьючу, но делаем это аккуратно - не просто future.set_result
        # а call_soon_threadsafe - т.е. плланируем в основном потоке ioloop вызов future.set_result'
        # в ближайшее возможное время
        ioloop.call_soon_threadsafe(future.set_result, 'OK')

    async def foo():
        print('start foo')

        # запускаем нашу штуковину в отдельном потоке и даём ей нашу фьючу, которую просигналим после выполнения
        future = ioloop.create_future()
        thread = threading.Thread(target=some_generic_io, args=(future,))
        thread.start()

        # наша фьюча - это awaitable, поэтому можно её вернуть в кишки asyncio
        await future

        print('end foo')

    tasks = [ioloop.create_task(foo())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


def test_other_thread_with_awaitable():
    print("============= TEST OTHER THREAD WITH AWAITABLE ==================")

    ioloop = asyncio.new_event_loop()

    # Всё, написанное в примере выше, мы оборачиваем в свой awaitable объект
    class DoInSeparateThread:
        def __init__(self, target):
            self.target = target
            self.future = ioloop.create_future()
            self.thread = None

        def _thread_func(self):
            self.target()
            ioloop.call_soon_threadsafe(self.future.set_result, 'OK')

        def __await__(self):
            # объект может использоваться в await, когда он реализует __await__
            # Эта функция должна инициализировать что-то, чего будем ожидать, а потом
            # вернуть наружу генератор, который генерирует какой-то другой awaitable для asyncio

            # Итак, инициализируем ожидание (запускаем что-то)
            self.thread = threading.Thread(target=self._thread_func)
            self.thread.start()

            # Делаем генератор, который в этой точке возвращает другой awaitable
            # И здесь есть тонкость: если из __await__ выползает другой awaitable
            # то где-то эта рекурсия должна закончиться?
            # Какой самый низкоуровневый awaitable объект, с которым работает asyncio?
            # Это и есть acyncio.Future.
            # См. код asyncio - так или иначе все awaitable в asyncio генерируют acyncio.Future
            # Причём важно: это не значит, что все awaitable в питоне сводятся к acyncio.Future,
            # await - это независимая от asyncio конструкция, подробнее см. meta.py
            yield from self.future

            # Генератор заканчивается выбросом StopIteration с указанным значением. По смыслу - результат ожидания.
            return 'Very good!'

    def some_generic_io():
        time.sleep(1)

    async def foo():
        print('start foo')

        # Используем наш awaitable объект, которые инкапсулирует запуск some_generic_io в отдельном потоке
        # и отдаёт в asyncio фьючу для его ожидания
        res = await DoInSeparateThread(some_generic_io)

        print('res = {}'.format(res))
        print('end foo')

    tasks = [ioloop.create_task(foo())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


if __name__ == '__main__':
    test_bad()
    test_other_thread_with_future()
    test_other_thread_with_awaitable()
