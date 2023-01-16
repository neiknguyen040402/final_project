import math

from flask import render_template, request, redirect, url_for, flash, session
import utils
from hrms import app, login
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required
from hrms.admin import *
from hrms.models import *
from datetime import datetime
from sqlalchemy.sql import extract, text
from sqlalchemy import func, literal_column, or_
import hashlib

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/register", methods=["POST", "GET"])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar_path = None
#check unique ...
        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(full_name=full_name, username=username, password=password, email=email, avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mat khau khong khop !!!'
        except Exception as ex:
            err_msg = 'He thong co loi' + str(ex)
    return render_template('register.html', err_msg=err_msg)

@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect(url_for('home_logged'))
        else:
            err_msg = 'username hoặc password không chính xác'
    return render_template('login.html', err_msg=err_msg)


@app.route("/admin-login", methods=["POST"])
def signin_admin():

    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user=user)
    return redirect('/admin')

@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@app.route('/home')
@login_required
def home_logged():
    user = current_user
    employee = Employee.query.filter_by(id=user.employee_id).first()

    de = employee.department_id
    position = employee.position_id

    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id
    count_em_all = db.session.query(func.count(Employee.id)) \
        .join(Department, Department.id == Employee.department_id) \
        .filter(Department.manager == manager_id).first()

    count_em_active = db.session.query(func.count(Employee.id)) \
        .join(Account, Account.employee_id == Employee.id) \
        .join(Department, Department.id == Employee.department_id) \
        .filter(Department.manager == manager_id, Account.active == True).first()

    count_ideas = db.session.query(func.count(Idea.id)) \
        .join(Employee, Employee.id == Idea.employee_id) \
        .join(Department, Department.id == Employee.department_id) \
        .join(Active_type, Idea.active == Active_type.id) \
        .filter(Department.manager == manager_id, Idea.employee_id != current_user.employee_id,
                Active_type.active_name == "chờ duyệt").first()

    return render_template('user/index.html', de=de, position=position, count_em_all=count_em_all,
                           count_em_active=count_em_active, count_ideas=count_ideas)


#thông tin user chung

@app.route('/user/<username>')
@login_required
def user_detail(username):
    user = Account.query.filter_by(username=username).first_or_404()
    employee = utils.get_detail_info_employee(user.employee_id)
    return render_template('user/profile.html', employee=employee)

@app.route('/user/<username>/updatepro', methods=['GET', 'POST'])
@login_required
def user_updateprofile(username):
    if request.method == 'POST':
        user = Account.query.filter_by(username=username).first_or_404()
        account = Account.query.get(current_user.id)
        employee = Employee.query.get(user.employee_id)

        employee.full_name = request.form['full_name']
        employee.date_of_birth = request.form['date_of_birth']
        employee.gender = request.form['gender']
        employee.phone = request.form['phone']
        employee.address = request.form['address']
        employee.CCCD = request.form['CCCD']
        employee.bank_account = request.form['bank_account']
        employee.license = request.form['license']
        avatar_path = None
        # check unique ...
        avatar = request.files.get('avatar')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
            account.avatar = avatar_path

        db.session.add(employee)
        db.session.add(account)

        db.session.commit()
        flash("Cập nhật thông tin thành công !")

        return redirect(url_for('user_detail', username=username))

@app.route('/user/<username>/updatepass', methods=['GET', 'POST'])
@login_required
def user_updateppass(username):
    user = Account.query.filter_by(username=username).first_or_404()
    employee = utils.get_detail_info_employee(user.employee_id)
    err_msg = ""
    if request.method == 'POST':
        account = Account.query.get(current_user.id)

        current_pass = request.form.get('currentPass')
        new_pass = request.form.get('newPass')
        confirm_pass = request.form.get('confirmPass')

        current_pass_hash = str(hashlib.md5(current_pass.strip().encode('utf-8')).hexdigest())
        try:
            if current_pass_hash.strip().__eq__(account.password):
                if new_pass.strip().__eq__(confirm_pass.strip()):
                    account.password = str(hashlib.md5(new_pass.strip().encode('utf-8')).hexdigest())

                    db.session.add(account)
                    db.session.commit()
                    flash("Cập nhật thông tin thành công !")
                    return redirect(url_for('user_detail', username=username))
                else:
                    err_msg = 'Mật khẩu mới không khớp !!!'
            else:
                err_msg = "Mật khẩu hiện tại không chính xác !!!"
        except Exception as ex:
            err_msg = 'He thong co loi' + str(ex)

        return render_template('user/profile.html', err_msg=err_msg, employee=employee)

@app.route('/user/salaryboard')
@login_required
def user_salary():
    msg = ''
    user = current_user
    employee = Employee.query.filter_by(id=user.employee_id).first()
    if datetime.now().month == 1:
        month = request.args.get('month', 12)
        year = request.args.get('year', datetime.now().year - 1)
    else:
        month = request.args.get('month', datetime.now().month - 1)
        year = request.args.get('year', datetime.now().year)
    sa = utils.get_info_salary(employee.id, month, year)
    ov = utils.get_sum_overtime_in_month(employee.id, month, year)


    if ov is None:
        sum_hour_worked_over = 0
    else:
        sum_hour_worked_over = ov.sum_hour_worked_over

    if sa is None:
        msg = 'Không tra cứu được kết quả'
        sa = 0

    return render_template('user/salary.html', sa=sa, ov=sum_hour_worked_over, msg=msg)

@app.route('/user/checkinboard')
@login_required
def user_checkin():
    msg = ''
    user = current_user
    employee = Employee.query.filter_by(id=user.employee_id).first()
    employee_id = employee.id

    if datetime.now().month == 1:
        month = request.args.get('month', 12)
        year = request.args.get('year', datetime.now().year - 1)
    else:
        month = request.args.get('month', datetime.now().month - 1)
        year = request.args.get('year', datetime.now().year)

    # danh sach ngày đi làm
    qr = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                          func.group_concat(extract('day', Checkin.date).distinct())) \
        .join(Position, Employee.position_id == Position.id) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Checkin, Checkin.salary_id == Salary.id) \
        .filter(Employee.id == employee_id,
                extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year) \
        .group_by(Salary.id).all()

    #danh sách ngày nghỉ có phép
    qr2 = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                           func.group_concat(extract('day', Checkin.date).distinct())) \
        .join(Position, Employee.position_id == Position.id) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Checkin, Checkin.salary_id == Salary.id) \
        .filter(Employee.id == employee_id,
                extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year,
                Checkin.timekeeping_type == 1).all()

    month = int(month)
    year = int(year)
    date_no_work_in_month = utils.get_day_of_week(month, year)     # danh sách ngày không đi làm (VD: thứ 7, CN...)
    from calendar import monthrange
    num_date = monthrange(year, month)[1]          #số ngày trong tháng


    return render_template('user/checkin.html', qr=qr, qr2=qr2, day_off=date_no_work_in_month, month=month,
                           num_date=num_date, msg=msg)


@app.route('/user/idea')
@login_required
def user_idea():
    ideas = db.session.query(Idea.id, Idea.create_at, Idea_type.idea_name, Idea.describe, Idea.active, Active_type.active_name) \
        .join(Idea_type, Idea.idea_type_id == Idea_type.id) \
        .join(Active_type, Idea.active == Active_type.id) \
        .filter(Idea.employee_id == current_user.employee_id).all()
    list_idea_type = db.session.query(Idea_type.id, Idea_type.idea_name).all()
    return render_template('user/idea.html', ideas=ideas, list_idea_type=list_idea_type)

@app.route('/user/deleteidea/<int:id>')
@login_required
def delete_idea_user(id):
    idea = Idea.query.filter_by(id=id).first()

    if idea:
        db.session.delete(idea)
        db.session.commit()
    flash("Đã xóa ý kiến !")

    return redirect(url_for('user_idea'))


@app.route('/createidea', methods=["POST", "GET"])
@login_required
def create_idea():
    err_msg = ""
    if request.method.__eq__('POST'):
        create_at = request.form.get('create_date')
        idea_type_id = request.form.get('idea_type_id')
        describe = request.form.get('describe')

        new_idea = Idea(describe=describe, employee_id=current_user.employee_id, active=1,
                            idea_type_id=idea_type_id, create_at=create_at, accepted_by=0)

        db.session.add(new_idea)
        db.session.commit()
        flash('Đã thêm thành công !!!')
        return redirect(url_for('user_idea'))


    return render_template('user/idea.html', err_msg=err_msg)


@app.route('/user/form')
@login_required
def form():
    forms = db.session.query(Form.id, Form.file_name, Form.describe, Form.path, Form.create_at, Form.download).all()
    return render_template('user/form.html', forms=forms)

# thông tin user phòng nhân sự
# quản lý nhân viên
@app.route('/employeeboard')
@login_required
def employee_board():
    kw = request.args.get('keyword')

    if kw == '':
        kw = None

    employees = utils.get_employees(kw=kw)

    return render_template('user/personnel/employeelist.html', employees=employees)

@app.route('/createemployee', methods=["POST", "GET"])
@login_required
def create_employee():
    err_msg = ""
    if request.method.__eq__('POST'):
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        start_day = request.form.get('start_day')
        license = request.form.get('license')
        CCCD = request.form.get('CCCD')
        bank_account = request.form.get('bank_account')
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')

        muc_trinh_do = request.form.get('muc_trinh_do')
        nganh_dao_tao = request.form.get('nganh_dao_tao')
        chuyen_nganh = request.form.get('chuyen_nganh')
        nam_tot_nghiep = request.form.get('nam_tot_nghiep')
        xep_loai = request.form.get('xep_loai')
        chung_chi_khac = request.form.get('chung_chi_khac')

        create_by = current_user.employee_id
        avatar_path = None
        employee = Account.query.filter(Account.username.__eq__(username)).first()
        try:
            if employee:
                err_msg = 'Tên tài khoản đã tồn tại!!!'
            else:
                if password.strip().__eq__(confirm.strip()):
                    avatar = request.files.get('avatar')
                    if avatar:
                        res = cloudinary.uploader.upload(avatar)
                        avatar_path = res['secure_url']

                    utils.add_employee(full_name=full_name,
                                       email=email, avatar=avatar_path, date_of_birth=date_of_birth,
                                       gender=gender, phone=phone, address=address, start_day=start_day,
                                       license=license, CCCD=CCCD, bank_account=bank_account,
                                       department_id=department_id, position_id=position_id, create_by=create_by)
                    em = Employee.query.filter(Employee.CCCD.__eq__(CCCD)).first()
                    employee_id = em.id

                    utils.add_user(full_name=full_name, username=username, password=password, email=email,
                                   avatar=avatar_path, employee_id=employee_id)

                    utils.add_level(muc_trinh_do=muc_trinh_do, nganh_dao_tao=nganh_dao_tao, chuyen_nganh=chuyen_nganh,
                                    nam_tot_nghiep=nam_tot_nghiep, xep_loai=xep_loai, chung_chi_khac=chung_chi_khac,
                                    employee_id=employee_id)
                    flash('Đã thêm thành công !!')
                    return redirect(url_for('employee_board'))
                else:
                    err_msg = 'Mat khau khong khop !!!'
        except Exception as ex:
            err_msg = 'He thong co loi ' + str(ex)
    return render_template('user/personnel/employeelist.html', err_msg=err_msg)

@app.route('/<int:id>/editemployee', methods=["POST", "GET"])
@login_required
def edit_employee(id):
    employee = Employee.query.get(id)
    em = Employee.query.filter_by(id=id).first()

    if request.method.__eq__('POST'):
        if employee:
            employee.full_name = request.form.get('full_name')
            employee.date_of_birth = request.form.get('date_of_birth')
            employee.gender = request.form.get('gender')
            employee.phone = request.form.get('phone')
            employee.address = request.form.get('address')
            employee.start_day = request.form.get('start_day')
            employee.license = request.form.get('license')
            employee.CCCD = request.form.get('CCCD')
            employee.bank_account = request.form.get('bank_account')
            employee.department_id = request.form.get('department_id')
            employee.position_id = request.form.get('position_id')

            db.session.add(employee)
            db.session.commit()

            flash("Cập nhật thông tin thành công !")
            return redirect(url_for('employee_board'))
    return render_template('user/personnel/editEmployeeInfo.html', em=em)

@app.route('/<int:id>/deleteemployee', methods=['GET', 'POST'])
@login_required
def deleteemployee(id):
    employee = Employee.query.filter_by(id=id).first()
    account = Account.query.filter_by(employee_id=id).first()
    if request.method == 'POST':
        if employee and account:
            db.session.delete(employee)
            db.session.delete(account)
            db.session.commit()
            flash("Đã xóa thành công")
            return redirect(url_for('employee_board'))

    return render_template('user/personnel/deleteEmployee.html')

@app.route('/<int:id>/employeedetail')
@login_required
def employeeDetail(id):
    employee = utils.get_detail_info_employee(id)
    return render_template('user/personnel/detailInfo.html', employee=employee)

@app.route('/checkinboard')
@login_required
def checkin_board():
    if datetime.now().month == 1:
        month = request.args.get('month', 12)
        year = request.args.get('year', datetime.now().year - 1)
    else:
        month = request.args.get('month', datetime.now().month - 1)
        year = request.args.get('year', datetime.now().year)
    qr = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                          func.group_concat(extract('day', Checkin.date).distinct()))\
        .join(Position, Employee.position_id == Position.id)\
        .join(Salary, Salary.employee_id == Employee.id)\
        .join(Checkin, Checkin.salary_id == Salary.id)\
        .filter(extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year)\
        .group_by(Salary.id).all()

    qr2 = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                           func.group_concat(extract('day', Checkin.date).distinct()))\
        .join(Position, Employee.position_id == Position.id) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Checkin, Checkin.salary_id == Salary.id) \
        .filter(extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year,
                Checkin.timekeeping_type == 1).all()


    month = int(month)
    year = int(year)
    date_no_work_in_month = utils.get_day_of_week(month, year)
    from calendar import monthrange
    num_date = monthrange(year, month)[1]


    return render_template('user/personnel/checkinboard.html', qr=qr, qr2=qr2, day_off=date_no_work_in_month, month=month, num_date=num_date)


@app.route('/<int:id>/checkindetail')
@login_required
def checkin_detail(id):
    checkin = utils.get_checkin_list(id)

    return render_template('user/personnel/checkindetail.html', checkinlist=checkin)

# quản lý hợp đồng
@app.route('/contractboard')
@login_required
def contract_board():

    contracts = utils.get_contract()
    employees = db.session.query(Employee.id, Employee.full_name).all()

    return render_template('user/personnel/contractlist.html', contracts=contracts, listAllEmployees=employees)
#kiểm tra có hợp đồng chưa

@app.route('/createcontract', methods=["POST", "GET"])
@login_required
def create_contract():
    err_msg = ""
    if request.method.__eq__('POST'):
        employee_id = request.form.get('employee_id_ct')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        basic_salary = request.form.get('basic_salary')
        type = request.form.get('type')
        content = request.form.get('content')
        create_by = request.form.get('create_by')

        contract = Contract.query.filter(Contract.employee_id.__eq__(employee_id)).first()

        if contract:
            err_msg = 'Kiểm tra lại!!! Nhân viên này đã có hợp đồng!!!'
        else:
            new_contract = Contract(start_date=start_date, end_date=end_date, basic_salary=basic_salary,
                                    content=content, type=type, create_by=create_by, employee_id=employee_id)

            db.session.add(new_contract)
            db.session.commit()
            flash('Đã thêm thành công !!!')
            return redirect(url_for('contract_board'))


    return render_template('user/personnel/contractlist.html', err_msg=err_msg)

@app.route('/employeeleaveboard')
@login_required
def employee_leave_board():
    employee_id = request.args.get('employee_id')
    kw = request.args.get('keyword')

    if kw == '' or employee_id == '':
        kw = None
        employee_id = None

    employees = utils.get_employee_leave()

    return render_template('user/personnel/employeeleavelist.html', employees=employees)

# thông tin user phòng kế toán

@app.route('/salaryboard')
@login_required
def salary_board():
    month = request.args.get('month')
    employee_id = request.args.get('employee_id')
    kw = request.args.get('kw')
    department_id = request.args.get('department_id')

    if month == '' or employee_id == '' or kw == '' or department_id == '':
        month = None
        employee_id = None
        department_id = None
        kw = None

    salaries = utils.get_salary_board(employee_id=employee_id, month=month, kw=kw, department_id=department_id)

    return render_template('user/accountant/salarylist.html', salaries=salaries)


@app.route('/createsalary', methods=["POST", "GET"])
@login_required
def create_salary():
    employee_id = request.args.get('employee_id')
    if datetime.now().month == 1:
        month = 12
    else:
        month = datetime.now().date().month - 1
    year = datetime.now().date().year


    basic_salary = db.session.query(Contract.basic_salary).filter(Contract.employee_id.__eq__(employee_id)).first()

    sum_worked_hour = utils.get_sum_worked_hour(employee_id, month, year)
    overtime_hour = utils.get_sum_overtime_in_month(employee_id, month, year)
    sum_amount_reward_discipline = utils.sum_amount_reward_discipline_by_employee(employee_id, month, year)
    allowance_salary_query = db.session.query(Employee.id, (Allowance.petrol + Allowance.for_lunch + Allowance.other)). \
        join(Position, Employee.position_id.__eq__(Position.id)). \
        join(Allowance, Allowance.position_id.__eq__(Position.id)). \
        filter(Employee.id == employee_id).first()
    num_dependent = db.session.query(Family.num_dependent).filter(Family.employee_id.__eq__(employee_id)).first()

    if request.method == 'POST':
        emid = request.form.get('emid')
        bs = request.form.get('basic_salary')
        sWH = request.form.get('sum_worked_hour')
        oH = request.form.get('overtime_hour')
        sARD = request.form.get('sum_amount_reward_discipline')
        aSQ = request.form.get('allowance_salary_query')
        nD = request.form.get('num_dependent')
        tU = request.form.get('tam_ung')

        bs = float(bs)
        sARD = float(sARD)
        sWH = float(sWH)
        oH = float(oH)
        aSQ = float(aSQ)
        nD = float(nD)
        if tU == '':
            tU = 0
        else:
            tU = float(tU)

        BH = bs * (0.08 + 0.015 + 0.01)
        salary_suffer_tax = bs + oH * (bs / 196) * 1.2 + sARD + tU
        reduce = 11000000 + BH + nD * 4400000
        salary_cal_tax = salary_suffer_tax - reduce
        if salary_cal_tax < 0:
            salary_cal_tax = 0
        TAX_TNCN = 0.0

        if salary_cal_tax <= 5000000:
            TAX_TNCN = 0.05 * salary_cal_tax
        elif 5000000 < salary_cal_tax <= 10000000:
            TAX_TNCN = 0.1 * salary_cal_tax - 250000
        elif 10000000 < salary_cal_tax <= 18000000:
            TAX_TNCN = 0.15 * salary_cal_tax - 750000
        elif 18000000 < salary_cal_tax <= 32000000:
            TAX_TNCN = 0.2 * salary_cal_tax - 1650000
        elif 32000000 < salary_cal_tax <= 52000000:
            TAX_TNCN = 0.25 * salary_cal_tax - 3250000
        elif 52000000 < salary_cal_tax <= 80000000:
            TAX_TNCN = 0.30 * salary_cal_tax - 5850000
        else:
            TAX_TNCN = 0.35 * salary_cal_tax - 9850000

        salary_no_tax = (bs / 196) * sWH + oH * (bs / 196) * 1.2 + sARD + aSQ + tU
        net_salary = salary_no_tax - BH - TAX_TNCN

        date_cal = str(year) + '-' + str(month) + '-15'
        cal_for_mon = datetime.strptime(date_cal, '%Y-%m-%d')

        create_at = datetime.now()

        salary = Salary(sum_hour_worked=sWH, sum_salary=salary_no_tax, month=cal_for_mon, tax_thu_nhap=TAX_TNCN,
                        tax_bao_hiem=BH, net_salary=net_salary, tam_ung=tU, create_at=create_at, employee_id=emid)
        db.session.add(salary)
        db.session.commit()
        flash('Đã thêm thành công !!')
        return redirect(url_for('salary_board'))

    return render_template('user/accountant/createsalary.html', basic_salary=basic_salary,
                           sum_worked_hour=sum_worked_hour, num_dependent=num_dependent,
                           overtime_hour=overtime_hour, sum_amount_reward_discipline=sum_amount_reward_discipline,
                           allowance_salary_query=allowance_salary_query, month=month, year=year, employee_id=employee_id)



@app.route('/insuranceinfo')
@login_required
def get_info_insurance():
    return render_template('user/accountant/insuranceinfo.html')


# for manager
@app.route('/manager/overview')
@login_required
def get_overview():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id
    count_em_all = db.session.query(func.count(Employee.id)) \
        .join(Department, Department.id == Employee.department_id) \
        .filter(Department.manager == manager_id).first()


    count_em_active = db.session.query(func.count(Employee.id)) \
        .join(Account, Account.employee_id == Employee.id)\
        .join(Department, Department.id == Employee.department_id) \
        .filter(Department.manager == manager_id, Account.active == 1).first()

    return render_template('user/manager/index.html', count_em_all=manager_id)

@app.route('/manager/employeeboard')
@login_required
def employee_board_manager():
    kw = request.args.get('keyword')

    if kw == '':
        kw = None

    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    if kw is not None:
        employees = db.session.query(Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, extract('day', Employee.date_of_birth),
                                     extract('month', Employee.date_of_birth), extract('year', Employee.date_of_birth),
                                     Employee.address, Employee.start_day, Employee.license, Employee.CCCD,
                                     Employee.bank_account, Employee.gender, Department.department_name, Employee.phone) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(Department.manager == manager_id, or_(Employee.full_name.contains(kw), Employee.id.contains(kw),
                    Department.department_name.contains(kw)),
                    Employee.active == 1).all()

    else:
        employees = db.session.query(Employee.create_by, Position.position_name, Employee.id,
                                     Employee.full_name, Employee.email, extract('day', Employee.date_of_birth),
                                     extract('month', Employee.date_of_birth), extract('year', Employee.date_of_birth),
                                     Employee.address, Employee.start_day, Employee.license, Employee.CCCD,
                                     Employee.bank_account, Employee.gender, Department.department_name, Employee.phone) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Position, Position.id == Employee.position_id) \
            .filter(Department.manager == manager_id).all()

    return render_template('user/manager/employeelist.html', employees=employees)

@app.route('/manager/createemployee', methods=["POST", "GET"])
@login_required
def create_employee_manager():
    if request.method.__eq__('POST'):
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        license = request.form.get('license')
        CCCD = request.form.get('CCCD')
        bank_account = request.form.get('bank_account')
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')
        create_by = current_user.employee_id

        utils.add_employee(full_name=full_name, email=email, date_of_birth=date_of_birth,
                           gender=gender, phone=phone, address=address,
                           license=license, CCCD=CCCD, bank_account=bank_account,
                           department_id=department_id, position_id=position_id, create_by=create_by)

        flash('Đã thêm thành công !!')
        return redirect(url_for('employee_board_manager'))
    return render_template('user/manager/createemployee.html')


@app.route('/manager/<int:id>/editemployee', methods=["POST", "GET"])
@login_required
def edit_employee_manager(id):
    employee = Employee.query.get(id)
    em = Employee.query.filter_by(id=id).first()

    if request.method.__eq__('POST'):
        if employee:
            employee.full_name = request.form.get('full_name')
            employee.date_of_birth = request.form.get('date_of_birth')
            employee.gender = request.form.get('gender')
            employee.phone = request.form.get('phone')
            employee.address = request.form.get('address')
            employee.start_day = request.form.get('start_day')
            employee.license = request.form.get('license')
            employee.CCCD = request.form.get('CCCD')
            employee.bank_account = request.form.get('bank_account')
            employee.department_id = request.form.get('department_id')
            employee.position_id = request.form.get('position_id')

            db.session.add(employee)
            db.session.commit()

            flash("Cập nhật thông tin thành công !")
            return redirect(url_for('employee_board_manager'))
    return render_template('user/manager/editEmployeeInfo.html', em=em)

@app.route('/manager/<int:id>/deleteemployee', methods=['GET', 'POST'])
@login_required
def deleteemployee_manager(id):
    employee = Employee.query.filter_by(id=id).first()
    account = Account.query.filter_by(employee_id=id).first()
    contract = Contract.query.filter_by(employee_id=id).first()
    if employee and account:
        db.session.delete(account)
        db.session.delete(contract)
        db.session.delete(employee)
        db.session.commit()
        flash("Đã xóa thành công")
    return redirect(url_for('employee_board_manager'))

@app.route('/manager/accountboard')
@login_required
def account_board_manager():
    kw = request.args.get('kws')

    if kw == '':
        kw = None

    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    if kw is not None:
        accounts = db.session.query(Account.id, Account.username, Account.joined_date, Account.active,
                                    Account.user_role) \
            .join(Employee, Employee.id == Account.employee_id) \
            .join(Department, Employee.department_id == Department.id) \
            .filter(Department.manager == manager_id, or_(Account.username.contains(kw), Account.id.contains(kw))).all()
    else:
        accounts = db.session.query(Account.id, Account.username, Account.joined_date, Account.active, Account.user_role)\
            .join(Employee, Employee.id == Account.employee_id) \
            .join(Department, Employee.department_id == Department.id) \
            .filter(Department.manager == manager_id).all()

    return render_template('user/manager/accountlist.html', accounts=accounts)

@app.route('/manager/createaccount')
@login_required
def form_create_account_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    employees = db.session.query(Employee.id, Employee.full_name) \
        .join(Department, Employee.department_id == Department.id) \
        .filter(Department.manager == manager_id).all()

    return render_template('user/manager/createaccount.html', employees=employees)

@app.route('/manager/createaccount/real', methods=["POST", "GET"])
@login_required
def create_account_manager():
    err_msg = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        employee_id = request.form.get('employee_id')
        avatar_path = None

        em = Employee.query.filter_by(id=employee_id).first()

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(full_name=em.full_name, username=username, password=password, email=em.email,
                               avatar=avatar_path, employee_id=employee_id)
                flash("Thêm thành công !!!")
                return redirect(url_for('account_board_manager'))
            else:
                err_msg = 'Mật khẩu không khớp !!!'
        except Exception as ex:
            err_msg = 'Hệ thống có lỗi' + str(ex)
    return render_template('user/manager/createaccount.html', err_msg=err_msg)


@app.route('/manager/contractboard')
@login_required
def contract_board_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    contracts = db.session.query(Employee.id, Employee.full_name, Employee.position_id, Employee.department_id,
                                 Position.position_name, Department.department_name, Contract.id.label('contract_id'),
                                 Contract.basic_salary, Contract.start_date, Contract.end_date, Contract.create_by,
                                 Contract.type, Contract.content) \
        .join(Position, Employee.position_id == Position.id) \
        .join(Department, Employee.department_id == Department.id) \
        .join(Contract, Contract.employee_id == Employee.id) \
        .filter(Department.manager == manager_id).all()

    return render_template('user/manager/contractlist.html', contracts=contracts)


@app.route('/manager/createcontract')
@login_required
def form_create_contract_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    employees = db.session.query(Employee.id, Employee.full_name) \
        .join(Department, Employee.department_id == Department.id) \
        .filter(Department.manager == manager_id).all()

    return render_template('user/manager/createcontract.html', employees=employees)

@app.route('/manager/createcontract/real', methods=["POST", "GET"])
@login_required
def create_contract_manager():
    err_msg = ""
    if request.method.__eq__('POST'):
        employee_id = request.form.get('employee_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        basic_salary = request.form.get('basic_salary')
        type = request.form.get('type')
        content = request.form.get('content')
        create_by = current_user.username

        contract = Contract.query.filter(Contract.employee_id.__eq__(employee_id)).first()

        if contract:
            err_msg = 'Kiểm tra lại!!! Nhân viên này đã có hợp đồng!!!'
        else:
            new_contract = Contract(start_date=start_date, end_date=end_date, basic_salary=basic_salary,
                                    content=content, type=type, create_by=create_by, employee_id=employee_id)

            db.session.add(new_contract)
            db.session.commit()
            flash('Đã thêm thành công !!!')
            return redirect(url_for('contract_board_manager'))

    return render_template('user/manager/createcontract.html', err_msg=err_msg)



@app.route('/manager/positionboard')
@login_required
def position_board_manager():
    positions = db.session.query(Position.id, Position.position_name, Position.content).all()
    return render_template('user/manager/positionlist.html', positions=positions)

@app.route('/manager/checkinboard')
@login_required
def checkin_board_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    if datetime.now().month == 1:
        month = request.args.get('month', 12)
        year = request.args.get('year', datetime.now().year - 1)
    else:
        month = request.args.get('month', datetime.now().month - 1)
        year = request.args.get('year', datetime.now().year)
    qr = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                          func.group_concat(extract('day', Checkin.date).distinct()))\
        .join(Position, Employee.position_id == Position.id)\
        .join(Department, Employee.department_id == Department.id)\
        .join(Salary, Salary.employee_id == Employee.id)\
        .join(Checkin, Checkin.salary_id == Salary.id)\
        .filter(Department.manager == manager_id,
                extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year)\
        .group_by(Salary.id).all()

    qr2 = db.session.query(Employee.id, Employee.full_name, Position.position_name,
                           func.group_concat(extract('day', Checkin.date).distinct()))\
        .join(Position, Employee.position_id == Position.id) \
        .join(Department, Employee.department_id == Department.id) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Checkin, Checkin.salary_id == Salary.id) \
        .filter(Department.manager == manager_id,
                extract('month', Checkin.date) == month,
                extract('year', Checkin.date) == year,
                Checkin.timekeeping_type == 1).all()


    month = int(month)
    year = int(year)
    date_no_work_in_month = utils.get_day_of_week(month, year)
    from calendar import monthrange
    num_date = monthrange(year, month)[1]


    return render_template('user/manager/checkinboard.html', qr=qr, qr2=qr2, day_off=date_no_work_in_month, month=month, num_date=num_date)


@app.route('/<int:id>/manager/checkindetail')
@login_required
def checkin_detail_manager(id):
    checkin = utils.get_checkin_list(id)

    return render_template('user/manager/checkindetail.html', checkinlist=checkin)

@app.route('/manager/salaryboard')
@login_required
def salary_board_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    month = request.args.get('month')
    employee_id = request.args.get('employee_id')
    kw = request.args.get('kw')
    department_id = request.args.get('department_id')

    if month == '' or employee_id == '' or kw == '' or department_id == '':
        month = None
        employee_id = None
        department_id = None
        kw = None

    salaries = db.session.query(Employee.id, Employee.full_name, Department.department_name, Position.position_name,
                                Salary.id, Salary.sum_hour_worked, Salary.sum_salary,
                                extract('month', Salary.month), Salary.tax_thu_nhap, Salary.tax_bao_hiem,
                                Salary.net_salary, Salary.tam_ung) \
        .join(Salary, Salary.employee_id == Employee.id) \
        .join(Department, Department.id == Employee.department_id) \
        .join(Position, Position.id == Employee.position_id) \
        .filter(Department.manager == manager_id).all()

    return render_template('user/manager/salarylist.html', salaries=salaries)

@app.route('/manager/ideaboard')
@login_required
def idea_board_manager():
    manager_account = current_user
    manager = Employee.query.filter_by(id=manager_account.employee_id).first()
    manager_id = manager.id

    ideas = db.session.query(Employee.id, Employee.full_name, Idea.update_at, Idea_type.idea_name, Idea.id,
                             Idea.describe, Idea.active, Idea.accepted_by, Active_type.active_name, Account.full_name)\
            .join(Idea, Employee.id == Idea.employee_id) \
            .join(Department, Department.id == Employee.department_id) \
            .join(Idea_type, Idea.idea_type_id == Idea_type.id) \
            .join(Active_type, Idea.active == Active_type.id) \
            .join(Account, Account.employee_id == Idea.accepted_by, isouter=True) \
            .filter(Department.manager == manager_id, Employee.id != current_user.employee_id).all()

    return render_template('user/manager/idealist.html', ideas=ideas)

@app.route('/manager/acceptidea/<int:id>')
@login_required
def accept_idea(id):
    idea = Idea.query.get(id)

    idea.active = 2
    idea.accepted_by = current_user.id

    db.session.add(idea)
    db.session.commit()
    flash("Đề xuất đã được phê duyệt !")

    return redirect(url_for('idea_board_manager'))

@app.route('/manager/refuseidea/<int:id>')
@login_required
def refuse_idea(id):
    idea = Idea.query.get(id)

    idea.active = 3
    idea.accepted_by = current_user.id

    db.session.add(idea)
    db.session.commit()
    flash("Đề xuất đã được từ chối !")

    return redirect(url_for('idea_board_manager'))


@app.route('/manager/deleteidea/<int:id>')
@login_required
def delete_idea(id):
    idea = Idea.query.filter_by(id=id).first()

    if idea:
        db.session.delete(idea)
        db.session.commit()
    flash("Đã xóa ý kiến !")

    return redirect(url_for('idea_board_manager'))


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)