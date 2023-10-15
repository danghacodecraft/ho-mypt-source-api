from django.urls import path

from app.http.views.education_view import EducationView
from .http.views import *
from .http.views.health_view import HealthView
from .http.views.hr_view import *
from .http.views.kpi_view import *
from .http.views.education_view import *

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),
    # KPIs - KQCV
    path('add-info-kpi', KpiView.as_view({'post': 'add_info_kpi'})),
    path('update-info-kpi', KpiView.as_view({'post': 'update_info_kpi'})),

    path('show-working-schedule', HrView.as_view({'post': 'get_show_working_schedule'})),
    path('import-working-schedule', HrView.as_view({'post': 'post_import_working_schedule'})),
    path('export-working-schedule', HrView.as_view({'post': 'get_export_working_schedule'})),

    # salary
    path('salary', HrView.as_view({'post': 'salary'})),
    path('import-salary', HrView.as_view({'post': 'import_salary'})),


    # những api chỉ gọi nội bộ- không public
    path('get-all-fake-data-by-email', KpiView.as_view({'get': 'get_all_fake_data_by_email'})),
    path('update-all-fake-data-by-email', KpiView.as_view({'post': 'update_all_fake_data_by_email'})),
    path('update-all-fake-data-by-email', KpiView.as_view({'post': 'update_all_fake_data_by_email'})),
    path('get-info-value-kpi-by-type', KpiView.as_view({'get': 'get_info_value_kpi_by_type'})),
    # api xử lý cho tác vụ fix data emp_code = 0
    path('update-code-by-accountMBN', KpiView.as_view({'post': 'update_code_by_accountMBN'})),

    # những api chỉ xử lý riêng cho tác vục fix data emp_code = 0
    # api get accountMBN save by xlsx, chỉ gọi nội bộ để lấy json
    path('get-accountMBN-code-by-zero', KpiView.as_view({'get': 'get_accountMBN_code_by_zero'})),
    path('convert-xlsx-to-json', KpiView.as_view({'post': 'convert_xlsx_to_json'})),
    
    # education
    path('import-education', EducationView.as_view({'post': 'import_education'})),
    path('show-education', EducationView.as_view({'post': 'show_education'})),

]
