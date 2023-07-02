#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Установка sqlalchemy: sudo pip3 install sqlalchemy

Простейший hello world в sqlalchemy.
Демонстрируется связь объектов питона с таблицей базы данных и вообще принцип работы ORM в sqlalchemy

Взято из https://ru.wikibooks.org/wiki/SQLAlchemy
"""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    create_engine,
)

from sqlalchemy.orm import (
    mapper,
    sessionmaker
)


# Пока что это просто обычный класс с 3 полями, никак не связанный с sqlalchemy и БД
# Он далее будет использоваться для представления одной строки определённой таблицы
class User(object):
    def __init__(self, name=None, fullname=None, password=None):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        # здесь просто выводятся поля класса, и есть есть поле id, тогда оно тоже

        maybe_id = getattr(self, 'id')
        return "<User('{}','{}', '{}'){}>".format(
            self.name, self.fullname, self.password,
            {} if not maybe_id else ' id={}'.format(maybe_id)
        )


def main():
    # Все незнакомые слова и функции здесь - импортированы из sqlalchemy, см. импорты выше.

    # ================ Singleton-ы для работы с БД =========================
    # В create_engine мы указываем как подключаемся к базе данных. В данном случае это sqlite в памяти
    # если  echo=True - инициализирует питонячий logger и пишет в лог, включая то, какие запросы делает в БД
    engine = create_engine('sqlite:///:memory:', echo=True)
    metadata = MetaData()

    # ===================== Создаём таблицы===================================
    # Сначала делаем объект таблицы. Смысл очень близок к обычному CREATE TABLE в sql
    users_table = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('fullname', String),
        Column('password', String)
    )

    # все подготовленные таблицы (в данном случае одна) создаём в БД
    metadata.create_all(engine)

    # ===========================Маппинг класса User к таблице ==========================================
    # вот здесь начинается магия - привязываем наш до этого обычный питонячий клас User к таблице users_table
    # после чего этот класс становится необычным, и дальше при манипуляциях с этим классом можно синкаться
    # с таблицей средствами sqlalchemy
    print('object User before mapping: {}'.format(User().__dict__))
    # >>> object User before mapping: {'fullname': None, 'name': None, 'password': None}

    mapper(User, users_table)

    print('object User after mapping: {}'.format(User().__dict__))
    # >>> object User after mapping:
    # >>> {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x7fa9c93c0dd8>,
    # >>> 'fullname': None, 'password': None, 'name': None}

    # ================================== Сессия ===================================
    # Эти ещё одна пара системных объектов для работы с БД, это уже не синглтоны, а скорее скорее локальные объекты
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    # ============================= Добавляем запись с используем объекта user ===============================
    # Собственно здесь главное, ради чего всё замышлялось

    # Пока делаем объект в памяти
    user = User("Вася", "Василий", "qweasdzxc")

    # Прицепили его в sqlalchemy
    session.add(user)

    # Вот здесь происходит SQL-запрос.
    session.commit()

    # Кстати, session уммет и откатывать изменения, гуглить "sqlalchemy session rollback"

    # Прочитали из БД - видно что строка появилась
    print('read user: {}'.format(
        # Мы сказали, что, хотим запросить User, sqlalchemy поняла из какой таблицы надо брать
        # filter_by превращается в WHERE в SQL
        # first думаю понятно
        session.query(User).filter_by(name="Вася").first()
    ))
    # >>> read user: <User('Вася','Василий', 'qweasdzxc') id=1>
    # Заметим, что появилось id=1. Мы не добавляли поле id в класс User - это сделала sqlalchemy на стадии маппинга

    # ========================= Меняем запись используя тот же самый объект user ===============================
    # Достаточно просто поменять поле в объекте,
    # потому что, когда мы сказали session.add(user) - у session теперь есть ссылка на user.
    # Т.е. объект user это теперь кэш между пользовательским кодом и базой данных.
    user.fullname = "Пупкин"

    # При вызове commit наше изменение применится в базу, но почему мы его не делаем - см ниже
    # session.commit()

    print('read user: {}'.format(session.query(User).filter_by(name="Вася").first()))
    # >>> read user: <User('Вася','Пупкин', 'qweasdzxc') id=1>

    # После изменения записи не было commit, но прочиталось всё равно 'Пупкин'
    # Это потому что у sqlalchemy работает через кэш (наш объект user, про который она знает, как указывалоь выше).
    # Т.е. в данном случае реального взаимодействия с БД не происходило


if __name__ == "__main__":
    main()
