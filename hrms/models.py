from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from hrms import db
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum


class UserRole(UserEnum):  #địng nghĩa hằng số
    ADMIN = 1
    MANAGER = 2
    USERPER = 3
    USERACC = 4
    USER = 5

class Account(db.Model, UserMixin):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))


    def __str__(self):
        return self.full_name

class Department(db.Model):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(30), nullable=False)
    manager = Column(Integer, nullable=False)
    describe = Column(String(255))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    create_by = Column(Integer)
    employees = relationship('Employee', backref='department', lazy=True)

    def __str__(self):
        return self.department_name

class Employee(db.Model):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime, default=datetime.now())
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    start_day = Column(DateTime, default=datetime.now())
    license = Column(String(50))
    CCCD = Column(String(20), nullable=False)
    bank_account = Column(String(20), nullable=False)
    active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    create_by = Column(Integer)
    department_id = Column(Integer, ForeignKey('department.id'))
    position_id = Column(String(10), ForeignKey('position.id'))
    accounts = relationship('Account', backref='employee', lazy=True)
    salary = relationship('Salary', backref='employee', lazy=True)
    overtimes = relationship('Overtime', backref='employee', lazy=True)
    contracts = relationship('Contract', backref='employee', lazy=True)
    levels = relationship('Level', backref='employee', lazy=True)
    quitjobs = relationship('Quitjob', backref='employee', lazy=True)
    family = relationship('Family', backref='employee', lazy=True)
    reward_discipline = relationship('Reward_discipline', backref='employee', lazy=True)
    idea = relationship('Idea', backref='employee', lazy=True)

    def __str__(self):
        return self.full_name
#
class Salary(db.Model):
    __tablename__ = 'salary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sum_hour_worked = Column(Float, nullable=False)
    sum_salary = Column(Float, nullable=False)
    month = Column(DateTime, default=datetime.now())
    tax_thu_nhap = Column(Integer, nullable=False)
    tax_bao_hiem = Column(Integer, nullable=False)
    net_salary = Column(Float, nullable=False)
    tam_ung = Column(Float)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))
    checkins = relationship('Checkin', backref='salary', lazy=True)
    tax = relationship('Tax', backref='salary', lazy=True)


class Checkin(db.Model):
    __tablename__ = 'checkin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now())
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    hour_worked = Column(Float, nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    overtime_id = Column(Integer, ForeignKey('overtime.id'))
    salary_id = Column(Integer, ForeignKey('salary.id'))
    timekeeping_type = Column(Integer, ForeignKey('timekeeping_type.id'))


class Timekeeping_type(db.Model):
    __tablename__ = 'timekeeping_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timekeeping_type_name = Column(String(20), nullable=False)
    checkins = relationship('Checkin')


class Overtime(db.Model):
    __tablename__ = 'overtime'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now())
    hour_worked = Column(Float, nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))
    checkins = relationship('Checkin', backref='overtime', lazy=True)

class Tax(db.Model):
    __tablename__ = 'tax'

    id = Column(Integer, primary_key=True, autoincrement=True)
    BHXH = Column(Float, nullable=False)
    BHYT = Column(Float, nullable=False)
    BHTN = Column(Float, nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    salary_id = Column(Integer, ForeignKey('salary.id'))

class Contract(db.Model):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(DateTime, default=datetime.now())
    end_date = Column(DateTime, nullable=False)
    basic_salary = Column(Float, nullable=False)
    content = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    create_by = Column(String(50), nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))

class Level(db.Model):
    __tablename__ = 'level'

    id = Column(Integer, primary_key=True, autoincrement=True)
    muc_trinh_do = Column(String(50), nullable=False)
    nganh_dao_tao = Column(String(50), nullable=False)
    chuyen_nganh = Column(String(50), nullable=False)
    nam_tot_nghiep = Column(DateTime)
    xep_loai = Column(String(50))
    chung_chi_khac = Column(String(50))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))

class Quitjob(db.Model):
    __tablename__ = 'quitjob'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(250), nullable=False)
    ngay_quyet_dinh = Column(DateTime)
    ngay_nghi_viec = Column(DateTime)
    nguoi_quyet_dinh = Column(String(50))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))

class Position(db.Model):
    __tablename__ = 'position'

    id = Column(String(10), primary_key=True, nullable=False, unique=True)
    position_name = Column(String(50), nullable=False)
    content = Column(String(255))
    allowances = relationship('Allowance', backref='position', lazy=True)
    employees = relationship('Employee', backref='position', lazy=True)


class Allowance(db.Model):
    __tablename__ = 'allowance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    for_lunch = Column(Float)
    petrol = Column(Float)
    other = Column(Float)
    position_id = Column(String(10), ForeignKey('position.id'))

class Family(db.Model):
    __tablename__ = 'family'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num_dependent = Column(Integer, nullable=False)
    describe = Column(String(255))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))

class Reward_discipline(db.Model):
    __tablename__ = 'reward_discipline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.now())
    decision_makers = Column(Integer)
    title = Column(String(30))
    content = Column(String(255))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    employee_id = Column(Integer, ForeignKey('employee.id'))


class Idea(db.Model):
    __tablename__ = 'idea'

    id = Column(Integer, primary_key=True, autoincrement=True)
    describe = Column(String(255))
    accepted_by = Column(Integer, nullable=False)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    active = Column(Integer, ForeignKey('active_type.id'))
    idea_type_id = Column(Integer, ForeignKey('idea_type.id'))
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())

class Active_type(db.Model):
    __tablename__ = 'active_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    active_name = Column(String(50), nullable=False)
    idea = relationship('Idea', backref='active_type', lazy=True)

class Idea_type(db.Model):
    __tablename__ = 'idea_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_name = Column(String(50), nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())
    idea = relationship('Idea', backref='idea_type', lazy=True)

class Form(db.Model):
    __tablename__ = 'form'

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_name = Column(String(50), nullable=False)
    describe = Column(String(255))
    path = Column(String(255), nullable=False)
    download = Column(String(255), nullable=False)
    create_at = Column(DateTime, default=datetime.now())
    update_at = Column(DateTime, default=datetime.now())

if __name__ == '__main__':
    db.create_all()


