#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
Примеры запросов к БД на получение информации.
Как готовятся таблицы - см. предыдущие примеры
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
    __tablename__ = 'department_employee'
    department_id = Column(Integer, ForeignKey('department.id'), primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'), primary_key=True)


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    employees = relationship('Employee', secondary='department_employee')

    def __repr__(self):
        return 'Department({})'.format(self.name)


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    departments = relationship('Department', secondary='department_employee')

    def __repr__(self):
        return 'Employee({})'.format(self.name)


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

    # связываем записи
    physics_department.employees.append(sheldon)
    physics_department.employees.append(leonard)

    engineer_department.employees.append(leonard)
    engineer_department.employees.append(howard)

    astro_department.employees.append(howard)
    astro_department.employees.append(raj)

    # добавляем записи и скидываем в БД
    session.add_all([physics_department, engineer_department, astro_department, sheldon, leonard, howard, raj])
    session.commit()

    # =================== Запросы ======================================
    # Общая суть очень напоминает обычные SQL-ные операции на запросах.

    # ============= filter_by, оно же WHERE =============================
    print('filter_by:')
    for obj in session.query(Employee).filter_by(name='sheldon').all():
        print(obj)

    # ================= some fields ====================================
    print('\nsome fields:')
    for obj in session.query(Employee.id).all():
        print(obj)

    # ======================= JOIN =====================================
    """
    Вот тут запрос из двух таблиц (классы Employee, Department),
    а join делаем по полю relationship, которое лежит внутри Employee - Employee.departments.

    По смыслу со стороны пользователя это будет приджойнить таблицу Department в Employee (неважно как,
    мы можем даже не знать, что они связаны через 3-ю таблицу.

    По факту в SQL это будет что-то типа

    SELECT * FROM employee
        JOIN department_employee ON employee.id = department_employee.employee_id
        JOIN department ON department.id = department_employee.department_id

    Ну и в конце order_by как в sql
    """
    print('\njoin')
    for obj in session.query(Employee, Department).join(Employee.departments).order_by(Employee.name).all():
        print(obj)
    """
    Такой запрос в SQL бы вернул таблицу, которая состояла бы из колонок и первой и второй таблице.
    В ORM возвращается tuple из двух объектов:

    (Employee(howard), Department(engineer))
    (Employee(howard), Department(astro))
    (Employee(leonard), Department(engineer))
    (Employee(leonard), Department(physics))
    (Employee(raj), Department(astro))
    (Employee(sheldon), Department(physics))
    """

    # ======================= etc =====================================
    # Через цепочку можно использовать разные фичи SQL, по смыслу они тут такие же, даже group_by есть.
    # В общем если надо сделать что-то SQLное таким образом - быстро гуглится
    print('\netc')
    res = session.query(Employee, Department).join(Employee.departments).order_by(Employee.name).\
        group_by(Employee.name).limit(2).all()

    for obj in res:
        print(obj)


if __name__ == "__main__":
    main()
