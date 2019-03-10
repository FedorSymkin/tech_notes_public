#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Демонстрация отношений "один ко многому".

Есть таблица department - отделы. В каждом отделе может быть много employee - сотрудников, для
которых тоже отдельная таблица.

Если совсем коротко - в объекте, который "один" появляется поле со списком соответствующих ему объектов которых много.

Взято из
https://www.pythoncentral.io/overview-sqlalchemys-expression-language-orm-queries/
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine,
    ForeignKey
)

from sqlalchemy.ext.declarative import (
    declarative_base
)

from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    backref
)


Base = declarative_base()


# Используется декларативный подход, см. пример declarative
class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Вот тут указывается ForeignKey - привязка поля department_id из таблицы employee
    # к полю id из таблицы department. ForeignKey потому что department_id - это фактически
    # ключ но в другой таблице
    department_id = Column(Integer, ForeignKey('department.id'))

    # А тут создаётся объект отношения, т.е. у каждого Employee есть свой Department
    # который берётся из другой таблицы (это определяется первым аргументом в вызове relationship)
    # Здесь же указывается backref - это значит что sqlalchemy должен создать в Department поле, в котором будет
    # список всех Employee этого Department (хотя мы явно это поле не создавали)
    department = relationship(Department, backref=backref('employees', uselist=True))


def main():
    # =============== Готовим объекты для работы с БД, создаём таблицы =======================
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    # =================== Работаем с БД =======================
    # Создали пока что в памяти 2 объекта для двух таблиц
    john = Employee(name='john')
    stan = Employee(name='stan')
    it_department = Department(name='IT')

    # и связали их вот таким простым способом
    john.department = it_department
    stan.department = it_department

    # учитывая всё особенности того, как мы определили классы Department и Employee
    # sqlalchemy сделает запись в таблицах department и employee, причём для записи
    # в employee он укажет department_id на id-шник из department
    session.add(john)
    session.add(stan)
    session.add(it_department)
    session.commit()

    # ================== Проверяем =======================
    # Прочитали объект типа Department
    it = session.query(Department).filter(Department.name == 'IT').one()

    # И самое красивое место этого примера - у объекта Department появилось поле employees,
    # хотя явно мы его не прописывали в Department. Оно появилось когда мы объявили department = relationship(...
    print(it.employees)
    # >>> [<__main__.Employee object at 0x7f67c7c6b8d0>, <__main__.Employee object at 0x7f67c7c6b9b0>]

    print(type(it.employees))
    # >>> <class 'sqlalchemy.orm.collections.InstrumentedList'>
    # как видно employees это список наших объектов Employee

    print(', '.join([employee.name for employee in it.employees]))
    # >>> john, stan


if __name__ == "__main__":
    main()
