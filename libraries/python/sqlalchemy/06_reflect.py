#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
sqlalchemy умеет подтягивать уже существующую структуру базы данных и существующие таблицы.
Здесь пример как это делается

# https://www.pythoncentral.io/sqlalchemy-faqs/
"""


import sqlite3
import os

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer
)

from sqlalchemy.ext.declarative import (
    declarative_base
)

from sqlalchemy.orm import (
    sessionmaker
)


def make_native_db():
    # делаем просто обычным способом базу данных и сохраняем её в файл
    conn = sqlite3.connect("example.db")
    c = conn.cursor()
    c.execute('''
                  CREATE TABLE person
                  (id int PRIMARY KEY, name text, email text)
                  ''')
    c.execute("INSERT INTO person VALUES (1, 'john', 'john@example.com')")
    c.close()
    conn.commit()


Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return 'Person({}, {})'.format(self.name, self.email)


def main():
    # а здесь тащим базу через sqlalchemy
    if os.path.exists('example.db'):
        os.remove('example.db')

    make_native_db()

    engine = create_engine('sqlite:///example.db', echo=False)

    # Вот принципиальное место. Вместо create_all (как раньше)
    # делаем reflect и тем самым подтягиваем существующие данные
    Base.metadata.reflect(bind=engine)

    # А дальше как обычно
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    print("\nData:")
    for obj in session.query(Person).all():
        print(obj)

    """
    Data:
    Person(john, john@example.com)
    """


if __name__ == "__main__":
    main()
