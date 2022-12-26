from hrms import app, db
import utils
from flask import redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from hrms.models import Employee, Department, UserRole, Account, Idea, Salary



class EmployeeView(ModelView):
    column_display_pk = True
    can_view_details = True
    can_create = True
    can_edit = True
    can_export = True
    column_exclude_list = ['date_of_birth', 'start_day', 'license', 'CCCD', 'bank_account', 'create_at', 'create_by', 'update_at']
    column_labels = {
        'id': 'Mã nhân viên',
        'full_name': 'Họ tên',
        'date_of_birth': 'Ngày sinh',
        'gender': 'Giới tính',
        'phone': 'Số điện thoại',
        'address': 'Địa chỉ',
        'start_day': 'Ngày bắt đầu',
        'license': 'Bằng lái xe',
        'bank_account': 'Số tài khoản ngân hàng',
        'department': 'Phòng ban',
        'position': 'Chức vụ'
    }
    can_set_page_size = True
    page_size = 6

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
class DepartmentView(ModelView):
    column_display_pk = True
    can_create = True
    can_view_details = True
    can_edit = True
    can_export = True
    can_delete = True
    column_labels = {
        'id': 'Mã phòng',
        'department_name': 'Tên phòng',
        'manager': 'Quản lý',
        'describe': 'Mô tả',
        'create_at': 'Ngày tạo',
        'update_at': 'Ngày cập nhật',
        'create_by': 'Tạo bởi'
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class AccountView(ModelView):
    column_display_pk = True
    can_view_details = True
    can_create = True
    can_delete = True
    can_edit = True
    can_export = True
    column_exclude_list = ['full_name', 'password', 'avatar', 'create_at', 'create_by', 'update_at', 'employee']
    column_labels = {
        'id': 'Mã tài khoản',
        'username': 'Tên tài khoản',
        'active': 'Trạng thái',
        'joined_date':'Ngày tham gia',
        'user_role':'Quyền'
    }
    can_set_page_size = True
    page_size = 10

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class IdeaView(ModelView):
    can_create = False
    can_delete = True
    can_edit = True
    can_view_details = True
    column_labels = {
        'describe': 'Nội dung',
        'accepted_by': 'Duyệt bởi',
        'active': 'Trạng thái',
        'create_at': 'Ngày tạo',
        'update_at': 'Ngày cập nhật',
        'employee' : 'Nhân viên',
    }
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class SalaryView(ModelView):
    can_create = False
    can_delete = True
    can_edit = True
    can_export = True
    can_view_details = True
    column_labels = {
        'sum_hour_worked': 'Tổng giờ làm',
        'sum_salary': 'Tổng lương trước thuế',
        'month': 'Tháng',
        'tax_thu_nhap': 'Thuế thu nhập',
        'tax_bao_hiem': 'Bảo hiểm',
        'net_salary': 'Thực nhận',
        'tam_ung': 'Tạm ứng',
        'create_at': 'Ngày tạo',
        'update_at': 'Ngày cập nhật',
        'employee': 'Nhân viên',
    }
    can_set_page_size = True
    page_size = 10
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()

        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        sum_num_em = utils.get_num_em()
        sum_num_de = utils.get_num_de()
        sum_num_acc_active = utils.get_num_acc_active()
        sum_num_acc = utils.get_num_acc()
        count_em_in_de = utils.get_num_em_de()
        return self.render('admin/index.html', sum_num_em=sum_num_em, sum_num_de=sum_num_de,
                           sum_num_acc_active=sum_num_acc_active, sum_num_acc=sum_num_acc,
                           count_em_in_de=count_em_in_de)

admin = Admin(app=app, name="KKL Administration", template_mode='bootstrap4', index_view=MyAdminIndex())


admin.add_view(EmployeeView(Employee, db.session))
admin.add_view(DepartmentView(Department, db.session))
admin.add_view(AccountView(Account, db.session))
admin.add_view(IdeaView(Idea, db.session))
admin.add_view(SalaryView(Salary, db.session))
admin.add_view(LogoutView(name='Logout'))