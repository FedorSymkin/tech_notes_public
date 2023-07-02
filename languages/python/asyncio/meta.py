#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
https://sohabr.net/habr/post/359018/
Дублирую материал отсюда с дополнительными пояснениями.

Здесь демонстрируются некоторые вещи, лежащие в основе asyncio - приоткрывается свет на то, как работает
async / await.

Ключевые мысли:

1. async / await != asyncio, просто наиболее часто эти понятия использются вместе.
Но на самом деле async / await это некоторые синтаксические конструкции языка, которые под капотом генерируют нужные
примитивы, а уже эти примитивы используются в модуле asyncio. Иначе говоря async / await можно использовать отдельно,
без asyncio. Здесь показан пример как мог бы выглядеть asyncio изнутри при максимальном и схематичном упрощении

2. Упрощённо говоря await можно рассматривать как yield from. Есть некоторая разница (в плане ограничений),
но по смыслу это почти одно и то же

3. Самая ключевая мысль, вытекающая из прошлого пункта: await ничего не блокирует! А просто отдаёт управление
некоторому вызывающему коду (также как yield) и вместе с этим отдаёт инструкции как и когда надо эту корутину будить
Т.е. await aiolib.some_io_request(data) надо читать так:
    * Сделать какой-то some_io_request с данными data
    * Сделать типа yield из этой корутины с передачей управление обратно в event loop и инструкцией, когда
        нужно будить обратно эту корутину.
    * Т.е. назначение some_io_request - это опционально провести какую-то инициализацию i/o, и подготовить инструкции
        когда надо будить текущую сопрограмму.

4. async def делает из обычной функции корутину и позволяет изнутри использовать await

5. Отличия await от yield from: в общем случае await может принимать только объект awaitable,
    т.е. у которого есть __await__(). Из наиболее частых таких бывают три объекта - корутина, таска, и фьюча.
    Отличив в том, что yield from можно с обычным генератором, а await - нельзя. В данном коде это обошли путём
    выставления генератору флажка CO_ITERABLE_COROUTINE (тогда await начинает дружить с генератором),
    но это хак.

6. TODO: что должен реализовать и вернуть __await__?

"""

import datetime
import heapq
import types
import time

class Task:

    """Представляет, как долго сопрограмма должна ждать перед возобновлением выполнения.

    Операторы сравнения реализованы для использования в heapq.
    К сожалению, кортеж с двумя элементами не работает, потому что,
    когда экземпляры класса datetime.datetime равны, выполняется
    сравнение сопрограмм, а поскольку они не имеют методом, реализующих
    операции сравнения, возникает исключение.

    Считайте класс подобием о asyncio.Task/curio.Task.
    """

    def __init__(self, wait_until, coro):
        self.coro = coro
        self.waiting_until = wait_until

    def __eq__(self, other):
        return self.waiting_until == other.waiting_until

    def __lt__(self, other):
        return self.waiting_until < other.waiting_until


class SleepingLoop:

    """Event loop, сфокусированный на отложенном выполнении сопрограмм.

    Считайте класс подобием asyncio.BaseEventLoop/curio.Kernel.
    """

    def __init__(self, *coros):
        self._new = coros
        self._waiting = []

    def run_until_complete(self):
        # Запустить все сопрограммы.
        for coro in self._new:
            # Здесь последовательно запускаются все сопрограммы до тех пор пока не достигнут yield,
            # он же await в данном случае. Посте остановки кладём сопрограмму в очередь ожидающих
            wait_until = coro.send(None)
            heapq.heappush(self._waiting, Task(wait_until, coro))

        # Не прерывать выполнение, пока есть выполняющиеся сопроцедуры.
        while self._waiting:
            now = datetime.datetime.now()

            # Получаем сопрограмму с самым ранним временем возобновления.
            # В данном примере это просто очередь с приоритетом - кого надо разбудить раньше
            # Реальный asyncio, понятно, сложнее
            task = heapq.heappop(self._waiting)

            if now < task.waiting_until:
                # Мы оказались здесь раньше, чем нужно,
                # поэтому подождем, когда придет время возобновить сопрограмму.
                delta = task.waiting_until - now
                time.sleep(delta.total_seconds())
                now = datetime.datetime.now()

            # Время возобновить выполнение сопрограммы.
            try:
                # продолжаем программу - до тех пор пока не наткнёмся на следующий await
                # (он же yield) который вернёт нам новый wait_until
                wait_until = task.coro.send(now)
                heapq.heappush(self._waiting, Task(wait_until, task.coro))
            except StopIteration:
                # Сопрограмма завершена - больше там нет await (иначе говоря yeild-ов)
                pass


# sleep без декоратора вернёт обычный питоновский генератор (потому что внутри yield),
# а декоратор @types.coroutine к этому генератору назначит флажок, что он ещё и корутина (CO_ITERABLE_COROUTINE)
# при этом тип не меняется - sleep(N) вернёт по-прежнему генератор, но такой, который умеет работать с await,
# потому что флажок
@types.coroutine
def sleep(seconds):
    """Останавливает сопрограмму на указанное количество секунд.

    Считайте класс подобием asyncio.sleep()/curio.sleep().
    """
    now = datetime.datetime.now()
    wait_until = now + datetime.timedelta(seconds=seconds)
    # Останавливаем все сопроцедуры в текущем стэке. Тут необходимо
    # использовать ```yield```, чтобы создать сопрограмму на базе генератора,
    # а не на базе ```async```.

    # actual прилетает сюда из строки выше: wait_until = task.coro.send(now)
    actual = yield wait_until

    # Возобновляем стэк выполнения, возвращая время,
    # которое мы провели в ожидании.
    return actual - now


# Если тут убрать async, то будет ошибка 'await' outside async function
# Но если вместо await поставить yield from - всё будет работать норм
# Т.е. async здесь - просто синтаксическая штука, чтобы await можно было юзать вместо yield from
async def countdown(label, length, *, delay=0):  # вернёт <class 'coroutine'> потому что async def
    """
    Начинает обратный отсчет с секунд ```length``` и с задержкой ```delay```.
    Это обычно то, что реализует пользователь.
    """
    print(label, 'waiting', delay, 'seconds before starting countdown')

    """
    В строке delta = await sleep(delay) заключена вся магия. И тут несколько пунктов:

    1. sleep формально это не awaitable, это обычный генератор, но у него есть флажок,
       CO_ITERABLE_COROUTINE (см. декоратор над ним), поэтому await в данном случае под капотом превращается в
       yield from sleep(delay)

    2. Самое интересное, что мы тут ничего не ждём, а просто возвращаем управление
       очереди событий, которая уже сама будет управлять всяческим ожиданием.
       Если смотреть на это как на yield from sleep(delay), станет понятно, что тут мы вернули wait_until -
       точку во времени, до какого момента надо приостановить эту корутину.
    """
    delta = await sleep(delay)

    print(label, 'starting after waiting', delta)
    while length:
        print(label, 'T-minus', length)
        waited = await sleep(1)
        length -= 1
    print(label, 'lift-off!')


def main():
    """Запустить event loop с обратным отсчетом 3 отдельных таймеров.

    Это обычно то, что реализует пользователь.
    """

    loop = SleepingLoop(
        countdown('A', 5),
        countdown('B', 3, delay=2),
        countdown('C', 4, delay=1),
    )
    start = datetime.datetime.now()
    loop.run_until_complete()
    print('Total elapsed time is', datetime.datetime.now() - start)


if __name__ == '__main__':
    main()


"""
A waiting 0 seconds before starting countdown
B waiting 2 seconds before starting countdown
C waiting 1 seconds before starting countdown
A starting after waiting 0:00:00.000047
A T-minus 5
C starting after waiting 0:00:01.001220
C T-minus 4
A T-minus 4
B starting after waiting 0:00:02.001018
B T-minus 3
C T-minus 3
A T-minus 3
B T-minus 2
C T-minus 2
A T-minus 2
B T-minus 1
C T-minus 1
A T-minus 1
B lift-off!
C lift-off!
A lift-off!
Total elapsed time is 0:00:05.005210
"""
