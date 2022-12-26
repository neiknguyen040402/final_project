#các module hỗ trợ

from hrms import app, db
from hrms.models import Employee, Department, Account, UserRole, Salary, Tax, Overtime, Checkin, Position, Level, Contract, Allowance, Family, Reward_discipline

from sqlalchemy import func, or_
from sqlalchemy.sql import extract
import hashlib

def add_user(full_name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    account = Account(full_name=full_name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                employee_id=kwargs.get('employee_id'),
                avatar=kwargs.get('avatar'))

    db.session.add(account)
    db.session.commit()

def add_employee(full_name, department_id, position_id, CCCD, **kwargs):
    employee = Employee(full_name=full_name.strip(), email=kwargs.get('email'),
                        date_of_birth=kwargs.get('date_of_birth'), gender=kwargs.get('gender'),
                        phone=kwargs.get('phone'), address=kwargs.get('address'),
                        start_day=kwargs.get('start_day'), license=kwargs.get('license'),
                        CCCD=CCCD, bank_account=kwargs.get('bank_account'),
                        department_id=department_id, position_id=position_id, create_by=kwargs.get('create_by'))
    db.session.add(employee)
    db.session.commit()
def add_level(muc_trinh_do, nganh_dao_tao, chuyen_nganh, nam_tot_nghiep, xep_loai, chung_chi_khac, employee_id):
    level = Level(muc_trinh_do=muc_trinh_do, nganh_dao_tao=nganh_dao_tao,
                  chuyen_nganh=chuyen_nganh, nam_tot_nghiep=nam_tot_nghiep,
                  xep_loai=xep_loai, chung_chi_khac=chung_chi_khac, employee_id=employee_id)
    db.session.add(level)
    db.session.commit()

def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return Account.query.filter(Account.username.__eq__(username.strip()),
                                    Account.password.__eq__(password),
                                    Account.user_role.__eq__(role)).first()

def check_department(username):
    qr = db.session.query(Department.id, Department.department_name)\
        .join(Employee, Account.employee_id == Employee.id)\
        .join(Department, Employee.department_id == Department.id)\
        .filter(Account.username == username).first()
    return qr

def check_position(username):
    qr = db.session.query(Account.id, Position.id, Position.position_name)\
        .join(Employee, Account.employee_id == Employee.id)\
        .join(Position, Employee.position_id == Position.id)\
        .filter(Account.username.__eq__(username.strip())).first()
    return qr

def get_user_by_id(user_id):
    return Account.query.get(user_id)

def get_sum_overtime_in_month(employee_id, month, year):
    q = db.session.query(func.sum(Overtime.hour_worked).label('sum_hour_worked_over'))\
        .filter(extract('month', Overtime.date) == month,
                extract('year', Overtime.date) == year,
                Overtime.employee_id == employee_id)\
                .group_by(extract('month', Overtime.date)).first()
    return q

def get_info_salary(employee_id, month, year):

    q = db.session.query(Employee.id, Employee.full_name, extract('month', Salary.month), Salary.sum_hour_worked,
                         Salary.sum_salary, Salary.tax_bao_hiem, Salary.tax_thu_nhap, Salary.tam_ung, Salary.net_salary)\
                      .join(Salary, Salary.employee_id.__eq__(Employee.id))\
                      .filter(Employee.id == employee_id,
                              extract('month', Salary.month) == month,
                              extract('year', Salary.month) == year).first()

    return q

def get_employees(kw=None):


    if kw:
        employees = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                     Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                     Account.username, Employee.gender,
                                     Department.department_name, Account.active, Employee.phone) \
            .join(Account, Account.employee_id == Employee.id) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(or_(Employee.full_name.contains(kw), Employee.id.contains(kw),
                        Department.department_name.contains(kw)),
                    Employee.active == 1).all()

    if kw is None:
        employees = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                     Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                     Account.username, Employee.gender,
                                     Department.department_name, Account.active, Employee.phone)\
                                    .join(Account, Account.employee_id == Employee.id)\
                                    .join(Department, Department.id == Employee.department_id)\
                                    .join(Position, Position.id == Employee.position_id)\
                                    .filter(Employee.active == 1).all()

    return employees
def count_employees(kw=None):
    if kw:
        employees = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                     Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                     Account.username, Employee.gender,
                                     Department.department_name, Account.active, Employee.phone) \
            .join(Account, Account.employee_id == Employee.id) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(or_(Employee.full_name.contains(kw), Employee.id.contains(kw),
                        Department.department_name.contains(kw)),
                    Employee.active == 1).all()

    if kw is None:
        employees = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                     Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                     Account.username, Employee.gender,
                                     Department.department_name, Account.active, Employee.phone) \
            .join(Account, Account.employee_id == Employee.id, isouter=True) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(Employee.active == 1).all()
    return len(employees)

def get_employee_leave():
    employees = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                 Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                 Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                 Account.username, Employee.gender,
                                 Department.department_name, Account.active, Employee.phone) \
        .join(Account, Account.employee_id == Employee.id) \
        .join(Department, Department.id == Employee.department_id) \
        .join(Position, Position.id == Employee.position_id) \
        .filter(Employee.active == 0).all()
    return employees

def get_detail_info_employee(employee_id):
    employee = db.session.query(Account.avatar, Employee.create_by, Position.position_name, Employee.id,
                                Employee.full_name, Employee.email, Employee.date_of_birth, Employee.address,
                                Employee.start_day, Employee.license, Employee.CCCD, Employee.bank_account,
                                Account.username, Employee.gender, Level.muc_trinh_do, Level.chuyen_nganh,
                                Department.department_name, Account.active, Employee.phone) \
        .join(Account, Account.employee_id == Employee.id) \
        .join(Department, Department.id == Employee.department_id) \
        .join(Position, Position.id == Employee.position_id) \
        .join(Level, Level.employee_id == Employee.id) \
        .filter(Employee.id.__eq__(employee_id)).first()

    return employee

def get_checkin_list(id):
    checkin = db.session.query(Employee.id, Employee.full_name, Checkin.date,
                               extract('hour', Checkin.time_in),
                               extract('minute', Checkin.time_in),
                               extract('second', Checkin.time_in),
                               extract('hour', Checkin.time_out),
                               extract('minute', Checkin.time_out),
                               extract('second', Checkin.time_out),
                               Checkin.hour_worked, Overtime.hour_worked.label('hour_over')) \
        .join(Salary, Employee.id == Salary.employee_id) \
        .join(Checkin, Checkin.salary_id == Salary.id) \
        .join(Overtime, Overtime.id == Checkin.overtime_id, isouter=True).filter(Employee.id == id).all()
    return checkin


def get_contract():
    contract = db.session.query(Employee.id, Employee.full_name, Employee.position_id, Employee.department_id,
                                Position.position_name, Department.department_name, Contract.id.label('contract_id'),
                                Contract.basic_salary, Contract.start_date, Contract.end_date, Contract.create_by,
                                Contract.type, Contract.content) \
        .join(Position, Employee.position_id == Position.id) \
        .join(Department, Employee.department_id == Department.id) \
        .join(Contract, Contract.employee_id == Employee.id).all()
    return contract

def sum_amount_reward_discipline_by_employee(employee_id, month, year):
    q = db.session.query(func.sum(Reward_discipline.amount)).filter(
        extract('month', Reward_discipline.date) == month,
        extract('year', Reward_discipline.date) == year,
        Reward_discipline.employee_id == employee_id) \
        .group_by(extract('month', Reward_discipline.date)).first()
    return q


# cho bang salary
def cal_tax_TNCN(employee_id, month, year):

    basic_salary = db.session.query(Contract.basic_salary).filter(Contract.employee_id.__eq__(employee_id)).first()
    overtime_hour = get_sum_overtime_in_month(employee_id, month, year)
    sum_amount_reward_discipline = sum_amount_reward_discipline_by_employee(employee_id, month, year)
    num_dependent = db.session.query(Family.num_dependent).filter(Family.employee_id.__eq__(employee_id)).first()

    BH = basic_salary * (0.08 + 0.015 + 0.01)
    salary_suffer_tax = basic_salary + overtime_hour.sum_hour_worked_over*(basic_salary/196)*1.2 \
                        + sum_amount_reward_discipline.sum_amount_reward_discipline
    reduce = 11000000 + BH + num_dependent * 4400000
    salary_cal_tax = salary_suffer_tax - reduce
    TAX = 0.0
    if salary_cal_tax <= 5000000:
        TAX = 0.05 * salary_cal_tax
    elif 5000000 < salary_cal_tax <= 10000000:
        TAX = 0.1 * salary_cal_tax - 250000
    elif 10000000 < salary_cal_tax <= 18000000:
        TAX = 0.15 * salary_cal_tax - 750000
    elif 18000000 < salary_cal_tax <= 32000000:
        TAX = 0.2 * salary_cal_tax - 1650000
    elif 32000000 < salary_cal_tax <= 52000000:
        TAX = 0.25 * salary_cal_tax - 3250000
    elif 52000000 < salary_cal_tax <= 80000000:
        TAX = 0.30 * salary_cal_tax - 5850000
    else:
        TAX = 0.35 * salary_cal_tax - 9850000
    return TAX

def get_sum_worked_hour(employee_id, month, year):
    q = db.session.query(func.sum(Checkin.hour_worked)) \
        .join(Salary, Checkin.salary_id == Salary.id) \
        .join(Employee, Salary.employee_id == Employee.id)\
        .filter(
        extract('month', Checkin.date) == month,
        extract('year', Checkin.date) == year,
        Employee.id == employee_id) \
        .group_by(extract('month', Checkin.date)).first()
    return q

def get_sum_salary_no_tax(employee_id, month, year):
    salary_id = db.session.query(Salary.id).filter(Salary.employee_id.__eq__(employee_id)).first()
    sum_worked_hour = get_sum_worked_hour(salary_id, month, year)
    basic_salary = db.session.query(Contract.basic_salary).filter(Contract.employee_id.__eq__(employee_id)).first()
    overtime_hour = get_sum_overtime_in_month(employee_id, month, year)
    sum_amount_reward_discipline = sum_amount_reward_discipline_by_employee(employee_id, month, year)
    allowance_salary_query = db.session.query(Employee.id, Allowance.petrol, Allowance.for_lunch, Allowance.other).\
        join(Position, Employee.position_id.__eq__(Position.id)).\
        join(Allowance, Allowance.position_id.__eq__(Position.id)).\
        filter(extract('month', Reward_discipline.date) == month,
               extract('year', Reward_discipline.date) == year).first()
    allowance_salary = sum(allowance_salary_query[1:])

    result = (basic_salary/196)*sum_worked_hour + overtime_hour.sum_hour_worked_over*(basic_salary/196)*1.2 \
             + sum_amount_reward_discipline.sum_amount_reward_discipline + allowance_salary
    return result

def get_net_salary(employee_id, month, year):
    basic_salary = db.session.query(Contract.basic_salary).filter(Contract.employee_id.__eq__(employee_id)).first()
    BH = basic_salary * (0.08 + 0.015 + 0.01)
    result = get_sum_salary_no_tax(employee_id, month, year) - BH - cal_tax_TNCN(employee_id, month, year)
    return result

def get_salary_board(employee_id=None, month=None, kw=None, department_id=None):
    if employee_id:
        salaries = db.session.query(Employee.id, Employee.full_name, Department.department_name, Position.position_name,
                                    Salary.id, Salary.sum_hour_worked, Salary.sum_salary,
                                    extract('month', Salary.month), Salary.tax_thu_nhap, Salary.tax_bao_hiem, Salary.net_salary,
                                    Salary.tam_ung) \
            .join(Salary, Salary.employee_id == Employee.id) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(Employee.id.__eq__(employee_id)).all()

    salaries = db.session.query(Employee.id, Employee.full_name, Department.department_name, Position.position_name,
                                Salary.id, Salary.sum_hour_worked, Salary.sum_salary,
                                extract('month', Salary.month), Salary.tax_thu_nhap, Salary.tax_bao_hiem,
                                Salary.net_salary, Salary.tam_ung) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Department, Department.id == Employee.department_id) \
        .join(Position, Position.id == Employee.position_id) \
        .all()
    return salaries

def add_salary(sum_hour_worked, sum_salary, month, tax_thu_nhap, tax_bao_hiem, net_salary, tam_ung, employee_id, **kwargs):
    salary = Salary(sum_hour_worked=sum_hour_worked, sum_salary=sum_salary, month=month,
                    tax_thu_nhap=tax_thu_nhap, tax_bao_hiem=tax_bao_hiem, net_salary=net_salary,
                    tam_ung=tam_ung, employee_id=employee_id, create_at=kwargs.get('create_at'),
                    update_at=kwargs.get('update_at'))

    db.session.add(salary)
    db.session.commit()

def get_day_of_week(month, year):
    from calendar import monthrange
    import datetime
    num_date = monthrange(year, month)[1]
    list_day_off = []
    for i in range(1, num_date + 1):
        if datetime.datetime(year, month, i).weekday() == 6 or datetime.datetime(year, month, i).weekday() == 5:
            list_day_off.append(i)
    return list_day_off

def get_name_by_id(employee_id):
    name = db.session.query(Employee.full_name).filter(Employee.id == employee_id).first()
    name = name.full_name
    return name


# for admin
def get_num_em():
    count = db.session.query(func.count(Employee.id)).filter(Employee.active == 1).first()
    return count
def get_num_de():
    count = db.session.query(func.count(Department.id)).first()
    return count
def get_num_acc_active():
    count = db.session.query(func.count(Account.id)).filter(Account.active == 1).first()
    return count
def get_num_acc():
    count = db.session.query(func.count(Account.id)).first()
    return count
def get_num_em_de():
    qr = db.session.query(Department.department_name, func.count(Employee.id))\
        .join(Department, Employee.department_id == Department.id)\
        .filter(Employee.active == 1)\
        .group_by(Department.id).all()
    return qr
# def get_contract():
#     contracts = db.
