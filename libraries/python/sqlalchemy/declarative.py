#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Декларативный подход к созданию таблицы и привязки класса к таблице.
Разница с hello_world.py здесь в том, что мы определяем класс User сразу с привязкой
с sqlalchemy. А mapper и отдельное создание таблицы делать уже не нужно

https://ru.wikibooks.org/wiki/SQLAlchemy
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine
)

from sqlalchemy.ext.declarative import (
    declarative_base
)

from sqlalchemy.orm import (
    sessionmaker
)


# От Base будут наследоваться все классы, которые мы хотим привязать к БД
Base = declarative_base()


class User(Base):
    """
    Здесь в отличие от hello_world.py уже не просто сферический класс в вакууме.
    Наследуемся от класса из SQLAlchemy, привязываем таблицу и её структуру
    """
    __tablename__ = 'users'

    # Заметим, что имя Column не указывается - оно выводится из имени поля
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    # В остальном всё так же как в hello_world
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        maybe_id = getattr(self, 'id')
        return "<User('{}','{}', '{}'){}>".format(
            self.name, self.fullname, self.password,
            {} if not maybe_id else ' id={}'.format(maybe_id)
        )


def main():
    # также как в hello_world
    engine = create_engine('sqlite:///:memory:', echo=True)

    # таблица создаётся здесь
    Base.metadata.create_all(engine)

    # сессия как обычно
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    # добавляем запись, проверяем что работает
    user = User("vasia", "Vasiliy Pypkin", "vasia2000")
    session.add(user)
    session.commit()
    print(session.query(User).filter_by(name="vasia").first())


if __name__ == "__main__":
    main()
