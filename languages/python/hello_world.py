# -*- coding: utf-8 -*-

# Несколько примеров разных hello world на python 3
# Запускать так: python3 ./hello_world.py


def default_hello_world():
    print("hello world default!")


def hello_world_to_stderr():
    # да, импорт можно делать не обязательно глобально
    import sys
    sys.stderr.write("hello world stderr!\n")


def hello_world_oop():
    # классы в питоне плюс минус соблюдают стандартную парадигму ООП
    class HelloWorldWriter:
        def __init__(self, text):
            self.text = text

        def write(self):
            print(self.text)

    w = HelloWorldWriter("hello world oop!")
    w.write()


def hello_world_comprehension_format():
    # одна из фишек питона - писать такие штуки в одну строку
    print('\n'.join(['Symbol: {}'.format(c) for c in "hello"]))
    
    # Выведет следующее:
    # Symbol: h
    # Symbol: e
    # Symbol: l
    # Symbol: l
    # Symbol: o


# Подставьте сюда свой hello world
default_hello_world()
