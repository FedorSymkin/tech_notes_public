#!/usr/bin/python3
# -*- coding: utf-8 -*-


def test_asyncio_base():
    """
    Несколько важных тезисов:
        * async def - корутины, единицы конкуретности
        * то, что стоит под async def - это обычная функция, но если её вызвать она вернёт корутину,
            аналогично тому как функция с yield при вызове возвращает генератор
        * await asyncio.something внутри этих async def -
            начать выполнять что-то долгое и отдать управление какой-то другой корутине
        * Важная штука - в something может быть sleep, http request, read file и проч, но надо чтобы оно
            было внутри asyncio, либо внутри совместимой библиотеки, например aiohttp. Если просто поставить
            requests.get - работать не будет
    """

    print("============= TEST ASYNC IO ==================")
    import asyncio

    async def foo():
        # Это функция которая возвращает корутину <class 'coroutine'>
        print('Running in foo')
        await asyncio.sleep(0)
        print('Explicit context switch to foo again')

    async def bar():
        # Это функция которая возвращает корутину <class 'coroutine'>
        print('Explicit context to bar')
        await asyncio.sleep(0)
        print('Implicit context switch back to bar')

    ioloop = asyncio.get_event_loop() # <class 'asyncio.unix_events._UnixSelectorEventLoop'>

    tasks = [
        ioloop.create_task(foo()), # <class '_asyncio.Task'>, create_task принимает корутину
        ioloop.create_task(bar()), # <class '_asyncio.Task'>
    ]
    # P.S. можно тауже asyncio.ensure_future(foo()), подробностей про разницу пока не будет

    wait_tasks = asyncio.wait(tasks)  # <class 'coroutine'>, wait - это тоже корутина

    ioloop.run_until_complete(wait_tasks)  # здесь мы передаём рутовую корутину
    ioloop.close()


if __name__ == '__main__':
    test_asyncio_base()
