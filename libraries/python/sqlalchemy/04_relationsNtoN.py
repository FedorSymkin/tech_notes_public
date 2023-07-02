#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Демонстрация отношений "многое ко многому".

Продолжение истории из relations1toN.py с таблицами department и employee.
Теперь допустим что у нас один и тот же человек может числиться в разных отделах

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
    relationship
)


Base = declarative_base()


class DepartmentEmployee(Base):
    # Здесь используется отдельная таблица связи employeeId - departmentId
    __tablename__ = 'department_employee'
    department_id = Column(Integer, ForeignKey('department.id'), primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'), primary_key=True)


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Создаём теперь явно объект типа relationship, в отличие от предыдущего случая (1toN)
    # Первый параметр 'Employee' - не класс а строка, а вместо backref используем secondary -
    # Говорим sqlalchemy через какую вспомогательную таблицу организуется связь многое-ко-многим.
    # И также в отличие от предыдущего случая relationship проставляется и в Department и в Employee
    employees = relationship('Employee', secondary='department_employee')


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Создаём теперь явно объект типа relationship, в отличие от предыдущего случая (1toN)
    # Первый параметр 'Employee' - не класс а строка, а вместо backref используем secondary -
    # Говорим sqlalchemy через какую вспомогательную таблицу организуется связь многое-ко-многим.
    # И также в отличие от предыдущего случая relationship проставляется и в Department и в Employee
    departments = relationship('Department', secondary='department_employee')


def main():
    # =============== Готовим объекты для работы с БД, создаём таблицы =======================
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    # =================== Работаем с БД =======================
    # создаём записи в памяти
    sheldon = Employee(name='sheldon')
    leonard = Employee(name='leonard')
    howard = Employee(name='howard')
    raj = Employee(name='raj')

    physics_department = Department(name='physics')
    engineer_department = Department(name='engineer')
    astro_department = Department(name='astro')

    # связываем записи - да, вот так просто
    physics_department.employees.append(sheldon)
    physics_department.employees.append(leonard)

    engineer_department.employees.append(leonard)
    engineer_department.employees.append(howard)

    astro_department.employees.append(howard)
    astro_department.employees.append(raj)

    # добавляем записи и скидываем в БД
    session.add_all([physics_department, engineer_department, astro_department, sheldon, leonard, howard, raj])
    session.commit()

    # ================== Проверяем =======================
    print("departments")
    for dep in session.query(Department):
        print(dep.name + ': ' + ', '.join([emp.name for emp in dep.employees]))

    print('')
    print("people")
    for emp in session.query(Employee):
        print(emp.name + ': ' + ', '.join([dep.name for dep in emp.departments]))

    """
        departments
        physics: sheldon, leonard
        engineer: leonard, howard
        astro: howard, raj

        people
        sheldon: physics
        leonard: engineer, physics
        howard: astro, engineer
        raj: astro
    """


if __name__ == "__main__":
    main()
